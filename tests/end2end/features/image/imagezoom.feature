Feature: Zooming the image displayed.

    Scenario: Zooming in.
        Given I open any image of size 200x200
        When I run zoom in
        Then the zoom level should be 1.1

    Scenario: Zooming out.
        Given I open any image of size 200x200
        When I run zoom out
        Then the zoom level should be 0.91

    Scenario: Zooming in and out.
        Given I open any image of size 200x200
        When I run zoom in
        And I run zoom out
        Then the zoom level should be 1
