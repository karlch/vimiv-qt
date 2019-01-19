Feature: Show current image name in window title

    Scenario: Show name of opened image in title
        Given I open any image
        Then the image name should be in the window title
