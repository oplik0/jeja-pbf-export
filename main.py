from export import export
from nodebb_import import nodebb_import
ex = export.scrape()


if __name__=="__main__":
    ex.export_to_file("export_result.json")
    im = nodebb_import.nodebb_import()
    im.import_topics()
    im.import_posts()
    im.import_character_sheet_template()
    print("Done!")
