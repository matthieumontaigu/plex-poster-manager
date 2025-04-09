def batch_edit(artworks_updater, all_movies, date_from, number_of_edits):
    all_movies_sorted = sorted(
        all_movies, key=lambda movie: movie["added_date"], reverse=True
    )
    edits = 0
    for movie in all_movies_sorted:
        if edits >= number_of_edits:
            break
        if movie["added_date"] > date_from:
            continue
        artworks_updater.update_artworks(movie)
        edits += 1
