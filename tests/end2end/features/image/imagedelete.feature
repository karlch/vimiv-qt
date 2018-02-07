Feature: Deleting an image in the current file list

    Scenario: Delete currently selected image
        Given I open 2 images
        When I run delete %
        Then the image should have the index 1
        And the filelist should contain 1 images
        And image_1.jpg should not be in the filelist

    Scenario: Delete any other image in the filelist
        Given I open 3 images
        When I run delete image_2.jpg
        Then the filelist should contain 2 images
        And image_2.jpg should not be in the filelist

    Scenario: Delete last image in filelist
        Given I open 2 images
        When I run goto 2
        And I run delete %
        Then the image should have the index 1
        And the filelist should contain 1 images
        And image_2.jpg should not be in the filelist

    Scenario: Delete only image in filelist
        Given I open any image
        When I run delete %
        Then image_1.jpg should not be in the filelist
        And the mode should be library
