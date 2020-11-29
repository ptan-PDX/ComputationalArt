import sys
import cv2
import numpy as np
# I reproduced a research paper in this python script.
# To understand the code, please read this paper first :https://igl.ethz.ch/projects/color-harmonization/harmonization.pdf

# FIXME: Type L shouldn't have a score that is smaller than type T.
templates = {
    'i': [0.05],
    'V': [0.26],
    'L': [0.05, 90, 0.22],
    'I': [0.05, 180, 0.05],
    'T': [0.5],
    'Y': [0.26, 180, 0.05],
    'X': [0.26, 180, 0.26],
}

a = 1
b = 0
# The smaller epsilon, the smaller c, the wider the bell curve, the less concentration on border.
epsilon = 0.000000000000000000000000001
c = np.sqrt(-180*180/2/np.log(epsilon))
def normalized_gaussian(x, a=1, b=0, c=32):
    return a * np.exp(-(x-b)*(x-b)/(2*c*c))

class HarmonicWheel:
    def __init__(self, type):
        self.type = type
        self.template_params = templates[type]
        self.update_alpha(alpha=0)

        # self.sectors == [[-9.0, 9.0]], for alpha=0, type i.
    
    def get_center_hue_by_border_id(self, border_id):
        sector_id = int(border_id / 2)
        h_center, w = self.get_center_hue_and_arc_of_sector(sector_id)
        if border_id % 2 == 0:
            # left
            w = -w
        return h_center, w

    def get_center_hue_and_arc_of_sector(self, sector_id):
        sector = self.sectors[sector_id]
        l, r = sector
        h_center = (l + r) / 2
        w = r - l
        # TODO: It may be outside [0, 360]
        return h_center, w

    def update_alpha(self, alpha):
        # Alpha as the center point of the first sector.
        self.alpha = alpha
        w = self.template_params[0] * 360
        left_border = alpha - w / 2
        right_border = alpha + w / 2

        if left_border < 0:
            left_border += 360
            right_border += 360

        sector = [left_border, right_border]
        self.sectors = [sector]

        if len(self.template_params) > 1:
            angle = self.template_params[1]
            w = self.template_params[2] * 360
            alpha = alpha + angle
            left_border = alpha - w / 2
            right_border = alpha + w / 2

            if left_border < 0:
                left_border += 360
                right_border += 360

            sector = [left_border, right_border]
            self.sectors.append(sector)

    def hue_in_sectors(self, h):
        # Return the nearest border id
        # TODO: we need to know the nearest border id
        border_id = None
        for i, sector in enumerate(self.sectors):
            lb, rb = sector
            c_hue = (lb + rb) / 2 
            if lb <= h <= rb:
                if h < c_hue:
                    border_id = i * 2
                else:
                    border_id = i * 2 + 1
            elif lb <= h + 360 <= rb:
                if h+360 < c_hue:
                    border_id = i * 2
                else:
                    border_id = i * 2 + 1
        return border_id
    
    def hue_to_border_arc(self, h):
        # border_id: 0 left of first sector, 1 right of first sector...
        # The arc shouldn't exceed +-180 degree.
        # +: counter-clockwise to border; -: clockwise to border
        #  < -180: d + 360
        #  > 180:  d - 360

        border_id = self.hue_in_sectors(h)
        if border_id is not None:
            return border_id, 0

        borders = []
        for s in self.sectors:
            borders += s

        d_nearest = 360
        border_id = -1
        for i, b in enumerate(borders):
            d = h - b
            if d < -180:
                d += 360
            if d > 180:
                d -= 360
            if abs(d) < abs(d_nearest):
                d_nearest = d
                border_id = i
        return border_id, d_nearest        
    
    def get_harmonic_score_of_pixel(self, pixel):
        h_pixel, s_pixel, _v_pixel = pixel
        _border_id, d = self.hue_to_border_arc(h_pixel)
        return abs(d) * s_pixel

    def preprocess_image(self, img_hsv):
        img_hsv = img_hsv.copy()
        img_hsv[:,:,0] = img_hsv[:,:,0] * 2
        img_hsv[:,:,1] = img_hsv[:,:,1] / 255
        img_hsv[:,:,2] = img_hsv[:,:,2] / 255
        return img_hsv
    
    def restore_image(self, img_hsv):
        img_hsv[:,:,0] = np.round(np.clip(img_hsv[:,:,0] / 2, 0, 180))
        img_hsv[:,:,1] = np.round(np.clip(img_hsv[:,:,1] * 255, 0, 255))
        img_hsv[:,:,2] = np.round(np.clip(img_hsv[:,:,2] * 255, 0, 255))
        return img_hsv.astype(np.uint8)

    def get_harmonic_score_image(self, img_hsv):
        # H: 0-360 by 2; S: [0,1], V: [0, 1]
        img_hsv = self.preprocess_image(img_hsv)
        h, w, _ = img_hsv.shape

        total_score = 0.
        for i in range(h):
            for j in range(w):
                pixel = img_hsv[i, j]
                score = self.get_harmonic_score_of_pixel(pixel)
                total_score += score

        return total_score

    def shift_hue(self, h_pixel, border_id):
        h_center, w = self.get_center_hue_by_border_id(border_id)

        # The distance shouldn't be larger than 180.
        h_distance = abs(h_center - h_pixel)
        if h_distance > 180:
            h_distance = 360 - h_distance
        weight = 1 - normalized_gaussian(h_distance)
        # print("h_center={:.1f} h_pixel={:.1f} h_distance={:.1f}  weight={:.1f}".format(h_center, h_pixel, h_distance, weight))
        # FIXME: check if the shifted hue value remains in [0, 360]
        h_prime = h_center + w/2 * weight

        # It may be larger than 360
        h_prime = h_prime % 360
        return h_prime

    def harmonize_image(self, img_hsv):
        img_hsv = self.preprocess_image(img_hsv)
        h, w, _ = img_hsv.shape
        for i in range(h):
            for j in range(w):
                h_pixel = img_hsv[i, j, 0]
                
                border_id, _d = self.hue_to_border_arc(h_pixel)
                h_prime = self.shift_hue(h_pixel, border_id)
                img_hsv[i,j,0] = h_prime

        img_hsv = self.restore_image(img_hsv)
        return img_hsv


# Web API
def load_resized_hsv_img(fname):
    img_orig = cv2.imread(fname)

    # H * 2 = degree [0, 360]
    # Source: https://docs.opencv.org/trunk/de/d25/imgproc_color_conversions.html#color_convert_rgb_hsv
    h, w, _ = img_orig.shape
    shortest_length = 30.
    scale_factor = min(h/shortest_length, w/shortest_length)
    # scale_factor = 1
    h_new = int(h / scale_factor)
    w_new = int(w / scale_factor)
    img_size = h_new * w_new
    img = cv2.resize(img_orig, (w_new, h_new))
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(float)
    return img_hsv, img_size


# Web API
def harmonize_image(fpath, fpath_har):
    # Load an image from local file system.
    img_hsv, img_size = load_resized_hsv_img(fpath)

    # Calculate score, only type X.
    wheel = HarmonicWheel(type='X')
    min_score = 180
    min_alpha = -1
    for alpha in range(0, 360):
        wheel.update_alpha(alpha)
        score = wheel.get_harmonic_score_image(img_hsv)
        score /= img_size
        if alpha == 0:
            score_orig = score
        if min_score > score:
            min_score = score
            min_alpha = alpha

    # Adjust the color.
    wheel.update_alpha(min_alpha)
    img_hsv_har = wheel.harmonize_image(img_hsv)
    img_bgr_har = cv2.cvtColor(img_hsv_har, cv2.COLOR_HSV2BGR)

    cv2.imwrite(fpath_har, img_bgr_har)

    return {'score_orig': format(score_orig,'.3f'), 'score': format(min_score,'.3f'), 'alpha': min_alpha}


if __name__ == "__main__":
    
    # fname = "example1_orig.jpg"
    # img_fname_har = "example_2_har_debug.jpg"

    #fname = "paper_images/image--005.jpg"
    # fname = "images/yellowGreen.jpg"
    fname = sys.argv[1]

    # fname = "paper_images/image--012.jpg"
    # img_fname_har = "chicken_debug.jpg"
    # L 87 9.489421820010046
    t_type = "L"
    alpha = 87

    img_orig = cv2.imread(fname)

    # H * 2 = degree [0, 360]
    # Source: https://docs.opencv.org/trunk/de/d25/imgproc_color_conversions.html#color_convert_rgb_hsv
    h, w, _ = img_orig.shape
    shortest_length = 30.
    scale_factor = min(h/shortest_length, w/shortest_length)
    # scale_factor = 1
    h_new = int(h / scale_factor)
    w_new = int(w / scale_factor)
    img = cv2.resize(img_orig, (w_new, h_new))
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(float)
    
    img_size = h_new * w_new
    
    best_type = best_alpha = None
    best_score = 180
    best_of_each_type = []
        # {"type":"i","alpha":0,"min_score":0},
        # {"type":"V","alpha":0,"min_score":0},
        # {"type":"L","alpha":0,"min_score":0},
        # {"type":"I","alpha":0,"min_score":0},
        # {"type":"T","alpha":0,"min_score":0},
        # {"type":"Y","alpha":0,"min_score":0},
        # {"type":"X","alpha":0,"min_score":0},
    

    for t_type in templates.keys():
        wheel = HarmonicWheel(t_type)
        min_score = 180
        min_alpha = -1
        for alpha in range(0, 360):
            wheel.update_alpha(alpha)
            score = wheel.get_harmonic_score_image(img_hsv)
            score /= img_size
            if min_score > score:
                min_score = score
                min_alpha = alpha
        if best_score > min_score:
            best_score = min_score
            best_type = t_type
            best_alpha = min_alpha
        template_best = {"type":t_type,"alpha":min_alpha,"min_score":min_score}
        best_of_each_type.append(template_best)

        print("Type {:s}, Alpha {:3d}, Score {:.2f}".format(t_type, min_alpha, min_score))
    print("Best: \nType {:s}, Alpha {:3d}, Score {:.2f}".format(best_type, best_alpha, best_score))
    print(best_of_each_type)
    # sys.exit(0)

    print("Harmonizing image...")
    # best_type = "I"
    # best_alpha = 45

    for type in best_of_each_type:
        best_type = type["type"]
        best_alpha = type["alpha"]
        score = type["min_score"]
        wheel = HarmonicWheel(best_type)
        wheel.update_alpha(best_alpha)

        img_hsv = cv2.cvtColor(img_orig, cv2.COLOR_BGR2HSV).astype(float)
        h_new, w_new, _ = img_hsv.shape
        img_size = h_new * w_new

        img_hsv_har = wheel.harmonize_image(img_hsv)
        img_bgr_har = cv2.cvtColor(img_hsv_har, cv2.COLOR_HSV2BGR)
        if best_type == "I":
            best_type = "bigI"
        img_fname_har = best_type +"_harmonized.jpg"
        cv2.imwrite(img_fname_har, img_bgr_har)

        img_hsv = cv2.cvtColor(img_bgr_har, cv2.COLOR_BGR2HSV).astype(float)

        # score = wheel.get_harmonic_score_image(img_hsv)
        # score /= img_size
        print("Score:", score)
