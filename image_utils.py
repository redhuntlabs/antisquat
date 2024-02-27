from PIL import Image
import imagehash

def are_images_similar(img_path1, img_path2, hash_size=3, cutoff=5):
    """Compare two images for similarity using image hashing.
    
    Args:
        img_path1 (str): Path to the first image.
        img_path2 (str): Path to the second image.
        hash_size (int): Hash size, higher value for more granularity.
        cutoff (int): Maximum Hamming distance (difference in hash bits).
                      Images will be considered similar if their difference is less or equal to this value.
    
    Returns:
        bool: True if images are similar, False otherwise.
    """
    # Load images
    image1 = Image.open(img_path1)
    image2 = Image.open(img_path2)

    # Generate hashes
    hash1 = imagehash.average_hash(image1, hash_size)
    hash2 = imagehash.average_hash(image2, hash_size)

    # Compare hashes
    if hash1 - hash2 <= cutoff:
        return True
    else:
        return False

