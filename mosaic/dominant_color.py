import scipy
import scipy.cluster
import scipy.misc


def get_dominant_color(img):
    """
    http://stackoverflow.com/a/3244061
    """

    array = scipy.misc.fromimage(img)
    shape = array.shape
    array = array.reshape(scipy.product(shape[:2]), shape[2])

    codes, _, = scipy.cluster.vq.kmeans(array.astype(float), 3)
    vecs, _ = scipy.cluster.vq.vq(array, codes)
    counts, _ = scipy.histogram(vecs, len(codes))

    index_max = scipy.argmax(counts)
    peak = codes[index_max].astype(int)
    color = ''.join(format(c, '02x') for c in peak)

    return color

