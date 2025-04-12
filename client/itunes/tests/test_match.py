import unittest

from client.itunes.match import get_matching_movie


class TestGetMatchingMovie(unittest.TestCase):

    def test_get_matching_slight_title_mismatch_1(self):
        candidates = [
            {
                "trackName": "Sonic Le Film 3",
                "artistName": "Jeff Fowler",
                "releaseDate": "2024-12-20T08:00:00Z",
            }
        ]
        title = "Sonic 3, le film"
        directors = ["Jeff Fowler"]
        year = 2024

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Sonic Le Film 3",
            "artistName": "Jeff Fowler",
            "releaseDate": "2024-12-20T08:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_slight_title_mismatch_2(self):
        candidates = [
            {
                "trackName": "Venom 3 : The Last Dance",
                "artistName": "Kelly Marcel",
                "releaseDate": "2024-10-30T07:00:00Z",
            }
        ]
        title = "Venom : The Last Dance"
        directors = ["Kelly Marcel"]
        year = 2024

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Venom 3 : The Last Dance",
            "artistName": "Kelly Marcel",
            "releaseDate": "2024-10-30T07:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_director_spelling_diff(self):
        candidates = [
            {
                "trackName": "Wicked",
                "artistName": "Jon Chu",
                "releaseDate": "2024-11-22T08:00:00Z",
            },
            {
                "trackName": "Scandaleusement vôtre",
                "artistName": "Thea Sharrock",
                "releaseDate": "2024-03-13T07:00:00Z",
            },
            {
                "trackName": "The Dark and the Wicked",
                "artistName": "Bryan Bertino",
                "releaseDate": "2020-09-18T07:00:00Z",
            },
            {
                "trackName": "Vilaine fille",
                "artistName": "Ayce Kartal",
                "releaseDate": "2017-01-01T08:00:00Z",
            },
        ]
        title = "Wicked"
        directors = ["Jon M. Chu"]
        year = 2024

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Wicked",
            "artistName": "Jon Chu",
            "releaseDate": "2024-11-22T08:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_multiple_directors(self):
        candidates = [
            {
                "trackName": "Vaiana 2",
                "artistName": "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr.",
                "releaseDate": "2024-11-27T08:00:00Z",
            }
        ]
        title = "Vaiana 2"
        directors = ["David G. Derrick Jr.", "Jason Hand", "Dana Ledoux Miller"]
        year = 2024

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Vaiana 2",
            "artistName": "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr.",
            "releaseDate": "2024-11-27T08:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_unknown_director(self):
        candidates = [
            {
                "trackName": "Monsieur Aznavour",
                "artistName": "Unknown",
                "releaseDate": "2024-10-23T07:00:00Z",
            }
        ]
        title = "Monsieur Aznavour"
        directors = ["Grand Corps Malade", "Mehdi Idir"]
        year = 2024

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Monsieur Aznavour",
            "artistName": "Unknown",
            "releaseDate": "2024-10-23T07:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_same_title_no_match(self):
        candidates = [
            {
                "trackName": "Le monde après nous",
                "artistName": "Louda Ben Salah-Cazanas",
                "releaseDate": "2022-04-20T07:00:00Z",
            }
        ]
        title = "Le Monde après nous"
        directors = ["Sam Esmail"]
        year = 2023

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {}
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_same_title_unknown_director(self):
        candidates = [
            {
                "trackName": "Hunter Killer",
                "artistName": "Donovan Marsh",
                "releaseDate": "2018-12-12T08:00:00Z",
            },
            {
                "trackName": "The Killer",
                "artistName": "John Woo",
                "releaseDate": "2024-08-22T07:00:00Z",
            },
            {
                "trackName": "Killers of the Flower Moon",
                "artistName": "Martin Scorsese",
                "releaseDate": "2023-10-20T07:00:00Z",
            },
            {
                "trackName": "Killer Elite (VF)",
                "artistName": "Gary McKendry",
                "releaseDate": "2011-10-26T07:00:00Z",
            },
            {
                "trackName": "Le bal des vampires",
                "artistName": "Roman Polanski",
                "releaseDate": "1968-04-01T08:00:00Z",
            },
            {
                "trackName": "Secret d'état",
                "artistName": "Michael Cuesta",
                "releaseDate": "2014-11-26T08:00:00Z",
            },
            {
                "trackName": "Killer Joe (VOST)",
                "artistName": "William Friedkin",
                "releaseDate": "2012-09-05T07:00:00Z",
            },
            {
                "trackName": "Dangereusement vôtre (A View to a Kill)",
                "artistName": "John Glen",
                "releaseDate": "1985-09-11T07:00:00Z",
            },
            {
                "trackName": "Permis de tuer (Licence to Kill)",
                "artistName": "John Glen",
                "releaseDate": "1989-08-16T07:00:00Z",
            },
            {
                "trackName": "Comment tuer son boss ?",
                "artistName": "Seth Gordon",
                "releaseDate": "2011-09-21T07:00:00Z",
            },
            {
                "trackName": "Killer Inside",
                "artistName": "Duncan Skiles",
                "releaseDate": "2021-06-03T07:00:00Z",
            },
            {
                "trackName": "Kiss & kill",
                "artistName": "Robert Luketic",
                "releaseDate": "2010-06-23T07:00:00Z",
            },
            {
                "trackName": "Tuer Bill: Volume 2",
                "artistName": "Quentin Tarantino",
                "releaseDate": "2004-04-16T07:00:00Z",
            },
            {
                "trackName": "Kill",
                "artistName": "Nikhil Nagesh Bhat",
                "releaseDate": "2024-09-11T07:00:00Z",
            },
            {
                "trackName": "Killer Joe (VF)",
                "artistName": "William Friedkin",
                "releaseDate": "2012-09-05T07:00:00Z",
            },
            {
                "trackName": "Comment tuer son boss 2",
                "artistName": "Sean Anders",
                "releaseDate": "2014-12-24T08:00:00Z",
            },
            {
                "trackName": "Open Source",
                "artistName": "Matt Eskandari",
                "releaseDate": "2020-08-21T07:00:00Z",
            },
            {
                "trackName": "Good Kill",
                "artistName": "Andrew Niccol",
                "releaseDate": "2015-04-22T07:00:00Z",
            },
            {
                "trackName": "Sniper 7 : Ultimate Kill",
                "artistName": "Claudio Fah",
                "releaseDate": "2017-10-02T07:00:00Z",
            },
            {
                "trackName": "Kill Bobby Z",
                "artistName": "John Herzfeld",
                "releaseDate": "2011-07-11T07:00:00Z",
            },
            {
                "trackName": "Kill Bill: Volume 1",
                "artistName": "Quentin Tarantino",
                "releaseDate": "2003-10-10T07:00:00Z",
            },
            {
                "trackName": "The Killer - Mission: Save the Girl",
                "artistName": "Choi Jae Hoon",
                "releaseDate": "2023-02-23T08:00:00Z",
            },
            {
                "trackName": "Kill Your Friends",
                "artistName": "Owen Harris",
                "releaseDate": "2015-12-02T08:00:00Z",
            },
            {
                "trackName": "Esther 2 : les origines",
                "artistName": "William Brent Bell",
                "releaseDate": "2022-08-17T07:00:00Z",
            },
            {
                "trackName": "Social Killer",
                "artistName": "Wilson Coneybeare",
                "releaseDate": "2019-03-25T07:00:00Z",
            },
            {
                "trackName": "Pulsions",
                "artistName": "Brian De Palma",
                "releaseDate": "1980-06-23T07:00:00Z",
            },
            {
                "trackName": "Kill Them All",
                "artistName": "Peter Malota",
                "releaseDate": "2017-06-12T07:00:00Z",
            },
            {
                "trackName": "Du Silence Et Des Ombres",
                "artistName": "Robert Mulligan",
                "releaseDate": "1963-03-16T08:00:00Z",
            },
            {
                "trackName": "Inside Ted : Dans la tête du serial killer",
                "artistName": "Amber Sealey",
                "releaseDate": "2023-01-31T08:00:00Z",
            },
            {
                "trackName": "Scorpio",
                "artistName": "Michael Winner",
                "releaseDate": "1973-04-11T08:00:00Z",
            },
            {
                "trackName": "Tueur d'élite",
                "artistName": "Sam Peckinpah",
                "releaseDate": "1975-12-17T08:00:00Z",
            },
            {
                "trackName": "Killers Anonymous",
                "artistName": "Martin Owen",
                "releaseDate": "2020-03-11T07:00:00Z",
            },
            {
                "trackName": "Comment tuer son Boss ? (Horrible Bosses: Totally Inappropriate Edition)",
                "artistName": "Seth Gordon",
                "releaseDate": "2011-08-17T07:00:00Z",
            },
            {
                "trackName": "A Day to Kill",
                "artistName": "Joseph Hahn",
                "releaseDate": "2014-06-18T07:00:00Z",
            },
            {
                "trackName": "Redivider",
                "artistName": "Tim Smit",
                "releaseDate": "2017-12-05T08:00:00Z",
            },
            {
                "trackName": "Kill List (VOST)",
                "artistName": "Ben Wheatley",
                "releaseDate": "2012-07-11T07:00:00Z",
            },
            {
                "trackName": "BTK Serial Killer",
                "artistName": "Stephen T. Kay",
                "releaseDate": "2012-05-28T07:00:00Z",
            },
            {
                "trackName": "Kill Me Please",
                "artistName": "Olias Barco",
                "releaseDate": "2010-11-03T07:00:00Z",
            },
            {
                "trackName": "I Am Not a Serial Killer",
                "artistName": "Billy O'Brien",
                "releaseDate": "2017-03-07T08:00:00Z",
            },
            {
                "trackName": "The Kill Room",
                "artistName": "Nicol Paone",
                "releaseDate": "2023-09-29T07:00:00Z",
            },
            {
                "trackName": "First Kill",
                "artistName": "Steven C. Miller",
                "releaseDate": "2018-09-04T07:00:00Z",
            },
            {
                "trackName": "Kill Dead Zombie!",
                "artistName": "Martijn Smits & Erwin van den Eshof",
                "releaseDate": "2013-04-17T07:00:00Z",
            },
            {
                "trackName": "3 Days to Kill",
                "artistName": "McG",
                "releaseDate": "2014-03-19T07:00:00Z",
            },
            {
                "trackName": "Le cercle noir",
                "artistName": "Unknown",
                "releaseDate": "2012-12-28T08:00:00Z",
            },
            {
                "trackName": "Funeral Killers",
                "artistName": "Renny Harlin",
                "releaseDate": "2020-05-11T07:00:00Z",
            },
            {
                "trackName": "Ghost Killers vs. Bloody Mary",
                "artistName": "Fabrício Bittar",
                "releaseDate": "2020-09-16T07:00:00Z",
            },
            {
                "trackName": "American murderer : La cavale sanglante",
                "artistName": "Matthew Gentile",
                "releaseDate": "2022-10-21T07:00:00Z",
            },
            {
                "trackName": "Kill Them All Again",
                "artistName": "Valeri Milev",
                "releaseDate": "2024-11-18T08:00:00Z",
            },
            {
                "trackName": "Crime de guerre (The Kill Team)",
                "artistName": "Dan Krauss",
                "releaseDate": "2019-10-25T07:00:00Z",
            },
            {
                "trackName": "In the Ams of a Killer",
                "artistName": "Robert L. Collins",
                "releaseDate": "1992-01-05T08:00:00Z",
            },
        ]
        title = "The Killer"
        directors = ["David Fincher"]
        year = 2023

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {}
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_multiple_candidates(self):
        candidates = [
            {
                "trackName": "Sherlock Holmes",
                "artistName": "Unknown",
                "releaseDate": "2010-02-03T08:00:00Z",
            },
            {
                "trackName": "Sherlock Holmes: A Game of Shadows",
                "artistName": "Guy Ritchie",
                "releaseDate": "2012-01-25T08:00:00Z",
            },
            {
                "trackName": "La Vie privée de Sherlock Holmes",
                "artistName": "Billy Wilder",
                "releaseDate": "1970-10-29T08:00:00Z",
            },
            {
                "trackName": "Young Sherlock Holmes: Le Secret de la Pyramide",
                "artistName": "Barry Levinson",
                "releaseDate": "1986-03-26T08:00:00Z",
            },
            {
                "trackName": "Sherlock Holmes & John Watson",
                "artistName": "Etan Cohen",
                "releaseDate": "2019-03-11T07:00:00Z",
            },
            {
                "trackName": "Sherlock Holmes : Le plus grand des détectives",
                "artistName": "Matthew Chow & Toe Yuen",
                "releaseDate": "2021-08-31T07:00:00Z",
            },
        ]
        title = "Sherlock Holmes"
        directors = ["Guy Ritchie"]
        year = 2010

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {
            "trackName": "Sherlock Holmes",
            "artistName": "Unknown",
            "releaseDate": "2010-02-03T08:00:00Z",
        }
        self.assertEqual(result, expected_result)

    def test_get_matching_movie_short_title_no_result(self):
        candidates = [
            {
                "trackName": "Air",
                "artistName": "Christian Cantamessa",
                "releaseDate": "2015-10-05T07:00:00Z",
            },
            {
                "trackName": "In the Air",
                "artistName": "Jason Reitman",
                "releaseDate": "2010-01-27T08:00:00Z",
            },
            {
                "trackName": "Le Dernier Maître de l'Air",
                "artistName": "M. Night Shyamalan",
                "releaseDate": "2010-07-01T07:00:00Z",
            },
            {
                "trackName": "Air",
                "artistName": "Anatol Schuster",
                "releaseDate": "2019-02-14T08:00:00Z",
            },
            {
                "trackName": "Millénium 3 : La reine dans le palais des courants d'air",
                "artistName": "Daniel Alfredson",
                "releaseDate": "2010-07-28T07:00:00Z",
            },
            {
                "trackName": "In the Air (VOST)",
                "artistName": "Jason Reitman",
                "releaseDate": "2010-01-27T08:00:00Z",
            },
            {
                "trackName": "Air Force One",
                "artistName": "Wolfgang Petersen",
                "releaseDate": "1997-07-25T07:00:00Z",
            },
            {
                "trackName": "La résistance de l'air",
                "artistName": "Fred Grivois",
                "releaseDate": "2015-06-17T07:00:00Z",
            },
            {
                "trackName": "2022 Un air d'Enfoirés",
                "artistName": "Les Enfoirés",
                "releaseDate": "2022-03-05T08:00:00Z",
            },
            {
                "trackName": "Air America",
                "artistName": "Roger Spottiswoode",
                "releaseDate": "1990-11-14T08:00:00Z",
            },
            {
                "trackName": "Thunderbirds : Les sentinelles de l'air",
                "artistName": "Jonathan Frakes",
                "releaseDate": "2005-12-26T08:00:00Z",
            },
            {
                "trackName": "Bronx à Bel-Air",
                "artistName": "Adam Shankman",
                "releaseDate": "2003-08-06T07:00:00Z",
            },
            {
                "trackName": "Next Day Air",
                "artistName": "Benny Boom",
                "releaseDate": "2009-05-08T07:00:00Z",
            },
            {
                "trackName": "Air Force",
                "artistName": "Howard Hawks",
                "releaseDate": "1945-02-07T07:00:00Z",
            },
            {
                "trackName": "Péril sur l'avion présidentiel",
                "artistName": "James Bamford",
                "releaseDate": "2024-02-13T08:00:00Z",
            },
            {
                "trackName": "Air Montserrat : Sur les traces d'un studio mythique (2021)",
                "artistName": "Gracie Otto",
                "releaseDate": "2021-06-14T07:00:00Z",
            },
            {
                "trackName": "Mirror Wars : Assaut sur Air Force One",
                "artistName": "Vassili Chiginsky",
                "releaseDate": "2012-02-01T08:00:00Z",
            },
            {
                "trackName": "Sur un air de Noël",
                "artistName": "Peter Sullivan",
                "releaseDate": "2021-10-19T07:00:00Z",
            },
            {
                "trackName": "La tête en l'air",
                "artistName": "Ignacio Ferreras",
                "releaseDate": "2013-01-30T08:00:00Z",
            },
            {
                "trackName": "Le Souffle Coupé",
                "artistName": "Amy Koppelman",
                "releaseDate": "2022-01-17T08:00:00Z",
            },
            {
                "trackName": "Un air du pays",
                "artistName": "Stefan Schwietert",
                "releaseDate": "2007-01-01T08:00:00Z",
            },
            {
                "trackName": "L'air de la mer rend libre",
                "artistName": "Nadir Moknèche",
                "releaseDate": "2023-10-04T07:00:00Z",
            },
            {
                "trackName": "…Enfants des courants d'air",
                "artistName": "Édouard Luntz",
                "releaseDate": "1959-01-01T08:00:00Z",
            },
            {
                "trackName": "Aida: The Epic Open Air Event",
                "artistName": "Ernst Märzendorfer, Eszter Szümegi, Kostatin Andreev & Cornelia Helfricht",
                "releaseDate": "2023-03-31T07:00:00Z",
            },
            {
                "trackName": "Natacha (presque) hôtesse de l'air",
                "artistName": "Noémie Saglio",
                "releaseDate": "2025-04-02T07:00:00Z",
            },
        ]
        title = "Air"
        directors = ["Ben Affleck"]
        year = 2023

        result = get_matching_movie(candidates, title, directors, year)
        expected_result = {}
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
