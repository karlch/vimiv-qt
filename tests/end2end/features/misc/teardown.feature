Feature: Various features related to teardown

    Scenario: Print text to stdout upon quit
        Given I start vimiv with -o vimiv
        And I capture output
        When I quit the application
        Then stdout should contain 'vimiv'

    Scenario: Print current path to stdout upon quit
        Given I open 2 images with -o %
        And I capture output
        When I quit the application
        Then stdout should contain 'image_01.jpg'

    Scenario: Print marked images to stdout upon quit
        Given I open 2 images with -o %m
        And I capture output
        When I run mark *
        And I quit the application
        Then stdout should contain 'image_01.jpg'
        And stdout should contain 'image_02.jpg'
