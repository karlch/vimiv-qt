Feature: Interaction with the system clipboard.

    Scenario: Copy basename from library path to clipboard.
        Given I open a directory with 1 paths
        When I run copy-name
        Then the clipboard should contain 'child_01'

    Scenario: Copy basename from library path to primary.
        Given I open a directory with 1 paths
        When I run copy-name --primary
        Then the primary selection should contain 'child_01'

    Scenario: Copy abspath from library path to clipboard.
        Given I open a directory with 1 paths
        When I run copy-name --abspath
        # /tmp from the directory in which tests are run
        Then the absolute path of child_01 should be saved in the clipboard

    Scenario: Copy basename from image path to clipboard.
        Given I open any image
        When I run copy-name
        Then the clipboard should contain 'image.jpg'

    Scenario: Copy and paste basename from library
        Given I open a directory with 1 paths
        When I run copy-name
        And I run paste-name
        Then the working directory should be child_01

    Scenario: Copy image to clipboard.
        Given I open any image
        When I run copy-image
        Then the clipboard should contain any image

    Scenario: Copy image to primary.
        Given I open any image
        When I run copy-image --primary
        Then the primary selection should contain any image

    Scenario: Copy image to clipboard and scale width.
        Given I open any image
        When I run copy-image --width=100
        Then the clipboard should contain an image with width 100

    Scenario: Copy image to clipboard and scale height.
        Given I open any image
        When I run copy-image --height=100
        Then the clipboard should contain an image with height 100

    Scenario: Copy image to clipboard and scale size.
        Given I open any image
        When I run copy-image --size=100
        Then the clipboard should contain an image with size 100
