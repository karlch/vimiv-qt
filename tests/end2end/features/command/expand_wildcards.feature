Feature: Expand wildcards when running commands

    Scenario: Expand % to the current path in the library
        Given I open a directory with 1 paths
        When I run !cp -r % %_bak
        Then the directory child_01_bak should exist

    Scenario: Expand % to current image in image mode
        Given I open any image
        When I run !cp % %.bak
        Then the file image.jpg.bak should exist

    Scenario: Do not expand % when escaped
        Given I open a directory with 1 paths
        When I run !cp -r \% %_bak
        Then the directory child_01_bak should not exist
        And a message should be displayed

    Scenario: Expand tilde to home directory
        Given I open a directory with 1 paths
        When I run !cp -r % ~/mypath.jpg
        Then the home directory should contain mypath.jpg

    Scenario: Do not expand tilde when escaped
        Given I open a directory with 1 paths
        When I run !cp -r % \~
        Then the directory ~ should exist

    Scenario: Expand %f to the list of paths in the library
        Given I open a directory with 2 paths
        When I run !rmdir %f
        Then the directory child_01 should not exist
        And the directory child_02 should not exist
