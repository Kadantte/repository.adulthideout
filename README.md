<p align="center">
  <img src="repository.adulthideout/resources/fanart.jpg" alt="AdultHideout 10th Anniversary" width="100%">
</p>

<h1 align="center">AdultHideout 1.0.16</h1>
<p align="center">
  <strong>Cartographer</strong><br>
  More paths. Better playback.<br>
  Released July 9, 2026.
</p>

AdultHideout started in **January 2016** as a tiny personal Kodi addon for one site. In its **10th Anniversary Year**, the 1.0.15 Harbor release made downloading and offline playback a first-class part of the addon. Cartographer builds on that foundation with broader source coverage and a more resilient runtime.

**Cartographer** adds twelve carefully integrated sources, fixes difficult playback and thumbnail paths, strengthens Cloudscraper compatibility, and refines Global Search and startup performance. The download and Offline videos foundation from Harbor remains available.

## Featured Highlights

### Download Manager. Built In.

Downloads now run as a managed background queue with clear progress, cancellation and retry controls. AdultHideout validates the destination before writing and remembers the workflow, so downloading feels like part of Kodi rather than an external workaround.

### Your Storage. Your Choice.

Choose a local folder or send downloads directly to **SMB** and **NFS** storage. The internal downloader remains the simple default, while FFmpeg, aria2 and JDownloader are available as optional backends for advanced setups.

### Offline Videos. Ready When You Are.

Enable **Offline videos** to replay completed downloads directly from AdultHideout. It stays disabled by default and only appears when you decide to use it.

### Twelve New Sources

**AnyPorn, WhoresHub, Fuqster, FreeonesTube, PornKTube, CollectionOfBestPorn, YourLust, XXBrits, PornXP, Sextu, Neporn and YouPerv.**

Every new integration was built around its actual site structure, with the navigation it supports: search, categories, models or performers, sorting and pagination. Playback prefers the best usable source and uses seek-safe proxy handling where the host requires it.

XFreeHD excludes login-only cards, XGroovy and TrannyVideosXXX include populated model directories, and SexVid ships with its real JPEG thumbnails.

## More Refined Everywhere

- **Global Search:** Fixed cross-search cache bleed, restored search scope correctly, kept playable results clean and removed the obsolete version-specific preset.
- **Cloudflare and Playback:** Repaired challenge-math handling for newer Python versions, improved protected artwork, and made slow or expiring CDN streams more dependable.
- **Navigation and Performance:** Cached repository metadata and indexed logo lookups to reduce repeated network and filesystem work.
- **Site Maintenance:** Updated domains and repaired pagination, categories, thumbnails and missing imports across several existing integrations.
- **Language Polish:** Removed hard-coded German fallback text from otherwise English navigation and dialogs.
- **Release Integrity:** Refreshed settings, logos, manifests, official hashes and repository metadata.

## Feature Focus: Cartographer

Downloading is intentionally simple on first use:

1. Choose **Download video** from a supported video's context menu.
2. Select a destination the first time the feature is used.
3. Follow progress in the Download Manager.
4. Replay the completed file from the optional **Offline videos** view.

Advanced integrations remain opt-in. A normal user can choose a folder and download without installing or configuring aria2, JDownloader or another external tool.

---

## Installation / Update

Install the **AdultHideout Repository** in Kodi, then install or update the video addon from it.

### Method 1: File Manager Source

1. Open Kodi and select the **Gear Icon**.
2. Go to **File manager** -> **Add source**.
3. Select `<None>` and enter `https://vashiel.github.io/repository.adulthideout/`.
4. Name the source `AdultHideout` and select **OK**.
5. Open **Add-ons** and select the **Package Icon**.
6. Choose **Install from zip file** -> **AdultHideout** -> `repository.adulthideout-1.0.4.zip`.
7. Open **Install from repository** -> **Adulthideout Video Addon Repository** -> **Video add-ons** -> **AdultHideout**.

### Method 2: Direct ZIP Download

1. Download [repository.adulthideout-1.0.4.zip](https://github.com/Vashiel/repository.adulthideout/raw/master/repository.adulthideout-1.0.4.zip).
2. In Kodi, open **Add-ons** -> **Package Icon** -> **Install from zip file**.
3. Select the downloaded repository ZIP.
4. Install **AdultHideout** from the repository.

### Method 3: Downloader App (Fire TV / Android TV)

1. Open the **Downloader** app.
2. Enter shortcode **`9480267`** or `aftv.news/9480267`.
3. Download and install `repository.adulthideout-1.0.4.zip`.
4. Install **AdultHideout** from the repository in Kodi.

---

## Repository Links

- **Homepage:** [vashiel.github.io/repository.adulthideout](https://vashiel.github.io/repository.adulthideout/)
- **Repository ZIP:** [repository.adulthideout-1.0.4.zip](https://github.com/Vashiel/repository.adulthideout/raw/master/repository.adulthideout-1.0.4.zip)
- **Source Code:** [github.com/Vashiel/repository.adulthideout](https://github.com/Vashiel/repository.adulthideout)
- **Issue Tracker:** [GitHub Issues](https://github.com/Vashiel/repository.adulthideout/issues)
- **Full Changelog:** [changelog.txt](plugin.video.adulthideout/changelog.txt)

## Disclaimer

AdultHideout is a Kodi video addon repository. It does not host third-party videos and is not affiliated with supported websites.

Content, streams and metadata are provided by third-party websites. The operators of those sites remain responsible for their content.

For repository issues, use GitHub Issues. For copyright complaints regarding content hosted on GitHub, GitHub's standard copyright process applies.

<details>
<summary><strong>Recent release archive</strong></summary>

### 1.0.14 "Featherlight" - 2026-06-14

- Reworked Global Search with source selection, presets, cached paging and playable-video-only results.
- Reduced the packaged addon size by more than half through vendor, cache and asset cleanup.
- Improved official-source checks, request resilience, settings and source coverage.

### 1.0.13 "Rangefinder" - 2026-06-13

- Added MyPornTape, FamilyPornHD, PornoBae, AllPornStream, Xtapes and CamgirlFap.
- Expanded resolver preferences, HLS handling and seek-safe local proxy playback.

### 1.0.12 "Signal Lock" - 2026-06-01

- Fixed Android compatibility for 85po, repaired LuxureTV and introduced FFmpeg recording.

</details>

## Contributing And Support

Submit bugs and feature requests through the issue tracker. Pull requests are welcome.

**AdultHideout started with Motherless. Ten years later, it is still here.**
