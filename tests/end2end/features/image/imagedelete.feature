Feature: Deleting an image in the current file list

    Scenario: Delete currently selected image
        Given I open 2 images
        When I run delete %
        And I wait for the working directory handler
        Then the image should have the index 1
        And the filelist should contain 1 images
        And image_01.jpg should not be in the filelist

    Scenario: Delete any other image in the filelist
        Given I open 3 images
        When I run delete image_02.jpg
        And I wait for the working directory handler
        Then the filelist should contain 2 images
        And image_02.jpg should not be in the filelist

    Scenario: Delete last image in filelist
        Given I open 2 images
        When I run goto 2
        And I run delete %
        And I wait for the working directory handler
        Then the image should have the index 1
        And the filelist should contain 1 images
        And image_02.jpg should not be in the filelist

    Scenario: Delete only image in filelist
        Given I open any image
        When I run delete %
        And I wait for the working directory handler
        Then image_01.jpg should not be in the filelist
        And the image widget should be empty

    Scenario: Delete multiple images
        Given I open 3 images
        When I run delete image_02.jpg image_03.jpg
        And I wait for the working directory handler
        Then the filelist should contain 1 images
        And image_02.jpg should not be in the filelist
        And image_03.jpg should not be in the filelist
        And the message
            'Deleted 2 images'
            should be displayed

    Scenario: Delete and undelete multiple images
        Given I open 3 images
        When I run delete image_02.jpg image_03.jpg
        And I wait for the working directory handler
        And I run undelete
        And I wait for the working directory handler
        Then the filelist should contain 3 images

    Scenario: Delete file that does not exist
        Given I open any image
        When I run delete this/is/not/an/image.jpg
        Then no crash should happen
        And the message
            'delete: No paths matching 'this/is/not/an/image.jpg''
            should be displayed

    Scenario: Undelete basename that does not exist
        Given I open any image
        When I run undelete not_a_basename.jpg
        Then no crash should happen
        And the message
            'undelete: File for 'not_a_basename.jpg' does not exist'
            should be displayed

    Scenario: Do not delete non-image file
        Given I start vimiv
        When I create the file 'not_an_image'
        And I run delete not_an_image
        Then the file not_an_image should exist
        And the message
            'delete: No images to delete'
            should be displayed

    Scenario: Keep limited filelist when deleting images
        Given I open 5 images
        When I run open image_03.jpg image_04.jpg image_05.jpg
        And I run delete %
        And I wait for the working directory handler
        Then the file image_03.jpg should not exist
        And the filelist should contain 2 images

    Scenario Outline: Delete image with special characters in filename
        Given I open the image '<name>'
        When I run delete %
        Then the file <name> should not exist

        Examples:
            | name    |
            | %.jpg   |
            | \.jpg   |
            | \%.jpg  |
            | \\%.jpg |
            | \%m.jpg |

    Scenario Outline: Undelete image with special characters in filename
        Given I open the image '<name>'
        When I run delete %
        And I run undelete
        Then no crash should happen
        And the file <name> should exist

        Examples:
            | name    |
            | %.jpg   |
            | \.jpg   |
            | \%.jpg  |
            | \\%.jpg |
            | \%m.jpg |
