# Usage

This is a simple GET API. Example:

/`nhanb`/`ajmg-nw`?dest=`https://link.to/redirect/%s`&format=`v%maj.%min.%pat%crap`

- `nhanb`: my github username
- `ajmg-nw`: my project repo
- `https://link.to/redirect/%s` (optional): the link to redirect to. `%s` will be replaced by the
  latest version string. Will return version string if link is not provided
- `v%maj.%min.%pat%crap` (optional): output format for version string

Demo server: https://github-latest.appspot.com/gitlabhq/gitlabhq

# Why?

So you can dynamically link to your latest version on static sites (GitHub Pages, project README,
etc.). Shameless plug: I'm using it on [ajmg-nw's README](https://github.com/nhanb/ajmg-nw) to link
to the latest binary releases on Amazon S3.
