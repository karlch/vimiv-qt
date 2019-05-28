Feature: Open different images and image formats

    Scenario: Error on invalid image formats
        Given I start vimiv
        When I open broken images
        Then no crash should happen

    # This does the magic to open all images in the directory
    # Therefore only the index, not the total number of images changes
    Scenario: Open single image using the open command
        Given I open 5 images
        When I run open image_03.jpg
        Then the filelist should contain 5 images
        And the image should have the index 3

    Scenario: Open multiple images using the open command
        Given I open 5 images
        When I run open image_01.jpg image_02.jpg
        Then the filelist should contain 2 images
