# Profile automation

The English introduction covers code, music, and games. Metrics displays activity and up to six languages from owned repositories, excluding forks. Public metrics are not a complete representation of work in private repositories.

## Setup

Create a dedicated classic GitHub personal access token without additional scopes and save it as the repository Actions secret `METRICS_TOKEN`. Do not reuse credentials with access to private work repositories. The repository-scoped `GITHUB_TOKEN` commits generated files.

After merging, run **Refresh profile** from Actions. It also runs daily at 04:17 UTC, after midnight in Santiago, and on relevant pushes to main. GitHub may delay scheduled runs. Without the secret, music still updates and no new Metrics image is linked. A failed render preserves an existing image.

## Daily music

The updater consumes `https://mariam.sh/api/discogs`, sharing the site's release selection instead of implementing a second random draw. The site hashes the date in `America/Santiago`; selection assumes an unchanged collection/order throughout the day. Repeated successful updates of the same payload produce identical text.

Only artist, title, date, and a validated Discogs release link are published. Text is HTML-escaped. Cover artwork and private Discogs credentials are not copied. Upstream failure preserves the previous pick and its date. Before the first successful fetch, the README links to the collection.

## Validation and references

Run `python3 -m unittest discover -s tests` for offline updater tests. Full rendering requires GitHub Actions and the dedicated secret.

- [Metrics setup and token requirements](https://github.com/lowlighter/metrics/blob/master/.github/readme/partials/documentation/setup/action.md)
- [Metrics manual output handling](https://github.com/lowlighter/metrics/blob/master/source/plugins/core/README.md)
