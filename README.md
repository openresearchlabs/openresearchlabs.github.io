# Turku Data Science Group website

## Add and edit team member information

Edit appropriate .yaml-files in data/team to add new team member information. The information will then be displayed in content/team.md file under the group specified by the .yaml-file name. For example, this will print information on all post-doc team members:

{{< team data="postdocs" >}}

Team member pictures should have face in center and should be close to a square. If no picture is provided a default placeholder image will be used. Add your picture in folder ./static/img/teampic and use a relative URL when pointing to the picture.

### Editing the templates and CSS files

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/team.html
- layouts/partials/team_partial.html

If you wish to edit flex-container item styles, see themes/hugo-universal-theme/static/css folder and file: style.default.css and rows starting with ".flex-container" and ".flex-item-".

More information about flex-containers:
- [StackOverflow](https://stackoverflow.com/questions/64853394/how-to-add-text-at-the-bottom-of-each-flexbox)
- [Aligning Items in a Flex Container (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout/Aligning_Items_in_a_Flex_Container)
- [A Complete Guide to Flexbox (CSS-Tricks)](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)

## Print items from bibliography

The site uses GitHub Actions to convert a .bib-file to a .json-file. Specific items from the bibliography, in this case an item that has "Salosensaari2021" as id (or key), can be printed with the following shortcode:

{{< articles id = "Salosensaari2021" >}}

If you wish to print items with specific keywords (in this case "opinion"), use:

{{< articles keyword = "opinion" >}}

Finally, ff you wish to print all items in the bibliography, simply use:

{{< articles >}}

### Editing the shortcodes and output styles

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/articles.html
- layouts/partials/publications_partial.html

For more information about shortcodes and partials, see following links: 
- [Hugo documentation](https://gohugo.io/templates/shortcode-templates/)
- For inspiration: loup-brun's [Hugo Cite](https://labs.loupbrun.ca/hugo-cite/)