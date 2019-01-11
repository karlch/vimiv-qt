Feature: Interaction with the system clipboard.

    Scenario: Copy basename from library path to clipboard.
        Given I open a directory with 1 paths
        When I run copy-name
        Then the clipboard should be set to child_01
 
    Scenario: Copy basename from library path to primary.
        Given I open a directory with 1 paths
        When I run copy-name --primary
        Then the primary selection should be set to child_01

    Scenario: Copy abspath from library path to clipboard.
        Given I open a directory with 1 paths
        When I run copy-name --abspath
        # /tmp from the directory in which tests are run
        Then the absolute path of child_01 should be saved in the clipboard

    Scenario: Copy basename from image path to clipboard.
        Given I open any image
        When I run copy-name
        Then the clipboard should be set to image.jpg

    Scenario: Copy and paste basename from library
        Given I open a directory with 1 paths
        When I run copy-name
        And I run paste-name
        Then the working directory should be child_01
