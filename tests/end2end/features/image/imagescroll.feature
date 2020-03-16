Feature: Scroll the current image

    Background:
        Given I open any image

    Scenario: Scroll to left edge
        When I run 10zoom in
        And I run scroll-edge left
        Then the image left-edge should be 0

    Scenario: Scroll to right edge
        When I run 10zoom in
        And I run scroll-edge right
        Then the image right-edge should be 300

    Scenario: Keep scroll position when size changes
        When I run 10zoom in
        And I run scroll-edge left
        And I resize the image
        Then the image left-edge should be 0
