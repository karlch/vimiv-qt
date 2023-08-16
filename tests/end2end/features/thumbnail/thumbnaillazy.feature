Feature: Lazy load thumbnails


    Background:
        Given I open 10 images
        And I enter thumbnail mode

    Scenario: Eager loading (default behavior)
        When I run 5scroll right
        Then there should be 10 rendered thumbnails
        And the first index should be 0
        And the last index should be 9
        And thumbnails should load in order of closeness to selected

    Scenario: Only display the selected thumbnail
        When I run set thumbnail.load_behind 0
        And I run set thumbnail.load_ahead 0
        And I run set thumbnail.unload_threshold 0
        And I run 5scroll right
        Then there should be 1 rendered thumbnails
        And the first index should be 5
        And the last index should be 5
        And thumbnails should load in order of closeness to selected

    Scenario: Display two thumbnails behind and all ahead
        When I run set thumbnail.load_behind 2
        And I run set thumbnail.unload_threshold 0
        And I run 5scroll right
        Then there should be 7 rendered thumbnails
        And the first index should be 3
        And the last index should be 9
        And thumbnails should load in order of closeness to selected

    Scenario: Display two thumbnails ahead and all behind
        When I run set thumbnail.load_ahead 2
        And I run 5scroll right
        Then there should be 8 rendered thumbnails
        And the first index should be 0
        And the last index should be 7
        And thumbnails should load in order of closeness to selected

    Scenario: Display two thumbnails ahead and behind
        When I run set thumbnail.load_ahead 2
        And I run set thumbnail.load_behind 2
        And I run set thumbnail.unload_threshold 0
        And I run 5scroll right
        Then there should be 5 rendered thumbnails
        And the first index should be 3
        And the last index should be 7
        And thumbnails should load in order of closeness to selected

    Scenario: Display two thumbnails ahead and behind but don't unload less than six tumbnails
        When I run set thumbnail.load_ahead 2
        And I run set thumbnail.load_behind 2
        And I run set thumbnail.unload_threshold 6
        And I run 5scroll right
        Then there should be 6 rendered thumbnails
        And the first index should be 3
        And the last index should be 7
        And thumbnails should load in order of closeness to selected
