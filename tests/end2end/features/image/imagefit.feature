Feature: Fitting the image displayed.

    Scenario: Fit landscape image to width.
        Given I open any image of size 2000x500
        When I run scale --level=fit
        Then the pixmap width should fit

    Scenario: Fit portrait image to height.
        Given I open any image of size 500x2000
        When I run scale --level=fit
        Then the pixmap height should fit

    Scenario: Fit landscape image to height.
        Given I open any image of size 2000x500
        When I run scale --level=fit-height
        Then the pixmap height should fit
        And the pixmap width should not fit

    Scenario: Fit portrait image to width.
        Given I open any image of size 500x2000
        When I run scale --level=fit-width
        Then the pixmap width should fit
        And the pixmap height should not fit

    Scenario: Fit image to float scale.
        Given I open any image of size 200x200
        When I run scale --level=2
        Then the pixmap width should be 400
        And the pixmap height should be 400

    Scenario: Do not overzoom small image.
        Given I open any image of size 200x200
        When I run scale --level=overzoom
        Then the pixmap width should be 200
        And the pixmap height should be 200

    Scenario: Scale down large image on overzoom.
        Given I open any image of size 2000x500
        When I run scale --level=overzoom
        Then the pixmap width should fit
