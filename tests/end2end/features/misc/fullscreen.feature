Feature: Toggle fullscreen mode.

    Background:
        Given I start vimiv

    Scenario: Enter fullscreen mode.
        When I run fullscreen
        Then the window should be fullscreen

    Scenario: Enter and leave fullscreen mode.
        When I run fullscreen
        And I run fullscreen
        Then the window should not be fullscreen
