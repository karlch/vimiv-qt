Feature: Rename paths

    Scenario: Rename images
        Given I open 2 images
        When I run rename * new_name
        Then the file new_name_001.jpg should exist
        Then the file new_name_002.jpg should exist

    Scenario: Keep mark state when renaming images
        Given I open 2 images
        When I run mark %
        When I run rename * new_name
        Then the file new_name_001.jpg should exist
        And new_name_001.jpg should be marked

    Scenario: Do not rename directories
        Given I open a directory with 2 paths
        When I run rename * new_directory
        Then no crash should happen
        And the directory new_directory_001 should not exist
