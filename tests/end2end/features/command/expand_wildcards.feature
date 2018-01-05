Feature: Expand wildcards when running commands

    Scenario: Expand % to the current path in the library
        Given I open a directory with 1 paths
        When I run !cp -r % %_bak
        And I wait for the command to complete
        Then the directory child_1_bak should exist

    Scenario: Expand % to current image in image mode
        Given I open any image
        When I run !cp % %.bak
        And I wait for the command to complete
        Then the file image.jpg.bak should exist

    Scenario: Do not expand % when escaped
        Given I open a directory with 1 paths
        When I run !cp -r \% %_bak
        And I wait for the command to complete
        Then the directory child_1_bak should not exist
        And a message should be displayed
