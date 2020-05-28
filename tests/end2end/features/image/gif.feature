Feature: Open and play animated gifs

    Background:
        Given I open an animated gif

    Scenario: Autoplay animated gif
        Then the animation should be playing

    Scenario: Pause animated gif
        When I run play-or-pause
        Then the animation should be paused
