Feature: Lazy load thumbnails

    Scenario: Eager loading (default behavior)
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        When I run 5scroll right
        Then the first index should be 0
        And the last index should be 9
        And there should be 10 rendered thumbnails

    Scenario: Only display the selected thumbnail
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        Then there should be 10 rendered thumbnails
        When I run set thumbnail.load_behind 0
        When I run set thumbnail.load_ahead 0
        When I run set thumbnail.unload_threshold 0
        When I run 5scroll right
        Then there should be 1 rendered thumbnails
        And the first index should be 5
        And the last index should be 5

    Scenario: Display two thumbnails behind and all ahead
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        Then there should be 10 rendered thumbnails
        When I run set thumbnail.load_behind 2
        When I run 5scroll right
        Then there should be 7 rendered thumbnails
        And the first index should be 3
        And the last index should be 9

    Scenario: Display two thumbnails ahead and all behind
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        Then there should be 10 rendered thumbnails
        When I run set thumbnail.load_ahead 2
        When I run 5scroll right
        Then there should be 8 rendered thumbnails
        And the first index should be 0
        And the last index should be 7

    Scenario: Display two thumbnails ahead and behind
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        Then there should be 10 rendered thumbnails
        When I run set thumbnail.load_ahead 2
        When I run set thumbnail.load_behind 2
        When I run 5scroll right
        Then there should be 5 rendered thumbnails
        And the first index should be 3
        And the last index should be 7

    Scenario: Display two thumbnails ahead and behind but don't unload less than six tumbnails
        Given I open 10 images without leading zeros in their name
        And I enter thumbnail mode
        Then there should be 10 rendered thumbnails
        When I run set thumbnail.load_ahead 2
        When I run set thumbnail.load_behind 2
        When I run set thumbnail.unload_threshold 6
        When I run 5scroll right
        Then there should be 6 rendered thumbnails
        And the first index should be 3
        And the last index should be 7
        And image_8.jpg should be in the rendered thumbnails
