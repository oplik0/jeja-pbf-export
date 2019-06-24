from export import export
from nodebb_import import nodebb_import
ex = export.scrape()


if __name__=="__main__":
    print("starting export...")
    ex.export_to_file("export_result.json")
    print("exported! Starting import...")
    im = nodebb_import.nodebb_import()
    im.import_topics()
    print("imported topics")
    im.import_posts()
    print("imported posts")
    im.import_character_sheet_template()
    print("Done!")
