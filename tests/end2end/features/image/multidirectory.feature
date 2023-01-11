Feature: Support for images from multiple directories in image mode

    # Reasonably complicated directory structure:
    # .
    # ├── dir1
    # │   ├── image_dir1_1.png
    # │   ├── image_dir1_2.png
    # │   └── image_dir1_3.png
    # ├── dir2
    # │   ├── also_image_dir2_1.png
    # │   └── also_image_dir2_2.png
    # └── dir3
    #     ├── more_image_dir3_1.png
    #     ├── more_image_dir3_2.png
    #     ├── more_image_dir3_3.png
    #     └── more_image_dir3_4.png

    Background:
        Given I open images from multiple directories

    Scenario: Open all images in single filelist
        Then the filelist should contain 9 images
        And the image should have the index 1
        # We sort all images according to the basename
        And the image number 1 should be also_image_dir2_1.png

    Scenario: Reverse sorting of images from multiple directories
        When I run set sort.reverse!
        Then the image should have the index 9
        And the image number 1 should be more_image_dir3_4.png
