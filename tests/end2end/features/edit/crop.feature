Feature: Crop an image.

    Background:
        Given I open any image of size 300x200

    Scenario: Enter crop widget
        When I run crop
        Then there should be 1 crop widget
        And the center status should include crop:

    Scenario: Enter crop widget with fixed aspectratio
        When I run crop --aspectratio=1:1
        Then there should be 1 crop widget
        And the center status should include crop:

    Scenario: Leave crop widget without changes
        When I run crop
        And I press '<escape>' in the crop widget
        Then there should be 0 crop widgets
        And the image size should be 300x200

    Scenario: Leave crop widget accepting changes
        When I run crop
        And I press '<return>' in the crop widget
        Then there should be 0 crop widgets
        And the image size should be 150x100

    Scenario Outline: Drag crop widget with the mouse
        When I run crop
        And I drag the crop widget by <dx>+<dy>
        Then the crop rectangle should be <geometry>

        Examples:
            | dx   | dy   | geometry        |
            | 0    | 0    | 150x100+75+50   |
            # small dx dy
            | 30   | -20  | 150x100+105+30  |
            # dx only as far as the image allows
            | 125  | 0    | 150x100+150+50  |
            # dy only as far as the image allows
            | 10   | -100 | 150x100+85+0   |
            # Ignored as dx/dy are outside of the image
            | 1000 | 1000 | 150x100+75+50   |
