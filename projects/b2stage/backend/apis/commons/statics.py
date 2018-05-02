# -*- coding: utf-8 -*-

TITLE = "EUDAT: B2STAGE HTTP-API"

FAVICO = "https://b2share.eudat.eu/favicon.ico"
FRAMEWORK = 'maxcdn.bootstrapcdn.com/bootstrap/4.0.0'
ICODE = 'Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm'
EXTRA_CSS_BASE = 'v4-alpha.getbootstrap.com/examples'

LOGOS = {
    'eudat': "https://www.eudat.eu/sites/default/files/EUDAT-logo.png",
    'b2stage': "https://www.eudat.eu/sites/default/files/logo-b2stage.png",
}

HEADER = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport"
        content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet"
        href="https://%s/css/bootstrap.min.css"
        integrity="sha384-%s" crossorigin="anonymous">
    <link rel="stylesheet"
        href="https://%s/narrow-jumbotron/narrow-jumbotron.css">
    <link rel="shortcut icon" href="%s"/>
    <title>%s</title>
</head>
<body>
 <div class="container">
      <div class="float-right">
        <table>
            <tr>
                <td> <img src='%s' width=75 </td>
                <td> <img src='%s' width=75 </td>
            </tr>
        </table>
      </div>
      <div class="header clearfix">
        <h2 class="text-muted">%s service</h2>
      </div>
""" % (
    FRAMEWORK, ICODE,
    FAVICO, EXTRA_CSS_BASE, TITLE,
    LOGOS.get('eudat'), LOGOS.get('b2stage'),
    TITLE
)

# TODO: get year from python
FOOTER = """
    <footer class="footer">
     <p>&copy; EUDAT 2018</p>
    </footer>
 </div>
</body>
</html>
"""
