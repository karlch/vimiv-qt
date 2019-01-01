Feature: Expand wildcards when running commands

    Scenario: Expand % to the current path in the library
        Given I open a directory with 1 paths
        When I run !cp -r % %_bak
        And I wait for the command to complete
        Then the directory child_01_bak should exist

    Scenario: Expand % to current image in image mode
        Given I open any image
        When I run !cp % %.bak
        And I wait for the command to complete
        Then the file image.jpg.bak should exist

    Scenario: Do not expand % when escaped
        Given I open a directory with 1 paths
        When I run !cp -r \% %_bak
        And I wait for the command to complete
        Then the directory child_01_bak should not exist
        And a message should be displayed

    Scenario: Expand * to the list of paths in the library
        Given I open a directory with 2 paths
        When I run !rmdir *
        And I wait for the command to complete
        Then the directory child_1 should not exist
        And the directory child_2 should not exist

    Scenario: Expand * to the list of images in image mode
        Given I open 2 images
        When I run !rm *
        And I wait for the command to complete
        Then the file image_01.jpg should not exist
        And the file image_02.jpg should not exist

    Scenario: Do not expand * when escaped
        Given I open a directory with 2 paths
        When I run !rmdir \*
        And I wait for the command to complete
        Then the directory child_01 should exist
        And the directory child_02 should exist
        And a message should be displayed
