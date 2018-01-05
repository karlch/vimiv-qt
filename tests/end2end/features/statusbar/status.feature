Feature: Display status information in the statusbar

    Scenario: Display image information
        Given I open 3 images
        Then the left status should include 1/3
        And the left status should include image_1.jpg
        And the right status should include IMAGE

    Scenario: Display library information
        Given I open any directory
        Then the left status should include directory
        And the right status should include LIBRARY

    Scenario: Display correct mode after switch
        Given I open any directory
        When I run enter image
        Then the right status should include IMAGE
