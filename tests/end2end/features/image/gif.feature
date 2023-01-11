@imageformats
Feature: Open and play animated gifs

    Background:
        Given I open an animated gif

    Scenario: Autoplay animated gif
        Then the animation should be playing

    Scenario: Pause animated gif
        When I run play-or-pause
        Then the animation should be paused

    Scenario: Do not rotate animated gif
        When I run rotate
        Then the message
            'rotate: File format does not support transform'
            should be displayed
