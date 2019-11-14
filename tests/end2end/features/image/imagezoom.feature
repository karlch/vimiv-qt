Feature: Zooming the image displayed.

    Scenario: Zooming in.
        Given I open any image of size 200x200
        When I run zoom in
        Then the zoom level should be 1.25

    Scenario: Zooming out.
        Given I open any image of size 200x200
        When I run zoom out
        Then the zoom level should be 0.8

    Scenario: Zooming in and out.
        Given I open any image of size 200x200
        When I run zoom in
        And I run zoom out
        Then the zoom level should be 1.0

    Scenario: Keep zoom level when reloading image.
        Given I open any image of size 200x200
        When I run zoom in
        And I run reload
        Then the zoom level should not be 1.0
