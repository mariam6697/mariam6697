# Profile automation

The English introduction covers code, music, and games. Metrics displays activity and up to six languages from owned repositories, excluding forks. Public metrics are not a complete representation of work in private repositories.

## Setup

Create a dedicated classic GitHub personal access token without additional scopes and save it as the repository Actions secret `METRICS_TOKEN`. Do not reuse credentials with access to private work repositories. The repository-scoped `GITHUB_TOKEN` commits generated files.

After merging, run **Refresh profile** from Actions. It also runs daily at 04:17 UTC, after midnight in Santiago, and on relevant pushes to main. GitHub may delay scheduled runs. Without the secret, music still updates and no new Metrics image is linked. A failed render preserves an existing image.

## Daily music

The updater queries the current public Discogs collection for `mmmariam` on each new date in `America/Santiago`. It reads the current collection size and fetches the selected page with an explicit added-date order, then saves one release in `daily-release.json`. No Discogs token or static copy of the collection is required.

The first successful pick is frozen for the day. Same-day reruns reuse the saved JSON without querying Discogs, even when records are added or removed. The next day's job queries the collection again, so those changes become eligible then. A release can repeat on consecutive days; a new daily draw does not guarantee a different result.

The website's `/api/discogs` endpoint is being updated to read this same JSON from the profile repository's `main` branch. Merge the profile PR and verify the published snapshot before deploying the site consumer. Failed upstream fetches leave the previous JSON and README untouched; their original date remains visible. On the first run there is no previous selection, so a collection link remains until generation succeeds.

The public JSON contains only the chosen release, date, and collection size, including a Discogs artwork URL for the existing site cover proxy. The profile displays artist/title/date and a validated release link, without artwork. API text is HTML-escaped in the README. No entire collection or private credentials are published. Requests that race with collection edits can fail; a later retry can succeed without replacing a successful same-day pick.

## Validation and references

Run `python3 -m unittest discover -s tests` for offline updater tests. Full rendering requires GitHub Actions and the dedicated secret.

- [Metrics setup and token requirements](https://github.com/lowlighter/metrics/blob/master/.github/readme/partials/documentation/setup/action.md)
- [Metrics manual output handling](https://github.com/lowlighter/metrics/blob/master/source/plugins/core/README.md)
