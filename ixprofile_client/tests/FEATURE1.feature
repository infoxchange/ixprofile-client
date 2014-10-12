Feature: Test fake profile server
  Scenario: Initialize profile server
    Given I have users in the fake profile server:
      | email           | subscribed | first_name | last_name | phone      | subscriptions          |
      | zoidberg@px.ea  | true       | John       | Zoidberg  | 1468023579 |                        |
      | hmcdoogal@px.ea | false      | Hattie     | McDoogal  |            |                        |
      | acalculon@px.ea | true       | Antonio    | Calculon  | 0292538800 |                        |
      | mendoza@mcog.fr | true       | Mendoza    | Unknown   |            | golden-condor,solaris  |
