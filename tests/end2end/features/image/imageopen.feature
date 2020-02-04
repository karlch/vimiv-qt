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

    Scenario: Open image using unix-style asterisk pattern expansion
        Given I open 11 images
        When I run open image_1*.jpg
        Then the filelist should contain 2 images

    Scenario: Open image using unix-style question mark pattern expansion
        Given I open 11 images
        When I run open image_1?.jpg
        Then the filelist should contain 2 images

    Scenario: Open image using unix-style group pattern expansion
        Given I open 12 images
        When I run open image_1[01].jpg
        Then the filelist should contain 2 images

    Scenario: Open path that does not exist
        Given I open any image
        When I run open not/a/path
        Then no crash should happen
        And the message
            'open: No paths matching 'not/a/path''
            should be displayed

    Scenario: Open invalid path
        Given I open any image
        When I run !touch not_an_image
        And I wait for the command to complete
        And I run open not_an_image
        Then no crash should happen
        And the message
            'open: No valid paths'
            should be displayed
