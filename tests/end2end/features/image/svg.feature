@imageformats
Feature: Open vector graphics

    Background:
        Given I open a vector graphic

    Scenario: Zoom vector graphic
        When I run zoom in
        Then no crash should happen
