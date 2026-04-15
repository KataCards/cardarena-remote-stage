# CHANGELOG


## v0.2.0-dev.3 (2026-04-15)

### Bug Fixes

- Fixed no sync url bug in go_home function
  ([`9bbca82`](https://github.com/KataCards/cardarena-remote-stage/commit/9bbca82dbee00afebd973298e6b76a5bfbbb3279))

* fix: fixed bug in go_home function

* chore: reomoved todo.txt


## v0.2.0-dev.2 (2026-04-14)

### Features

- Outsourced Middleware into its own file
  ([`693cebe`](https://github.com/KataCards/cardarena-remote-stage/commit/693cebe466049fe2a1ca6ffd1741448bfb3fca3a))


## v0.2.0-dev.1 (2026-04-14)

### Bug Fixes

- Fixed a build command issue
  ([`3a5e4e0`](https://github.com/KataCards/cardarena-remote-stage/commit/3a5e4e08e617dd938ab63548c9760f568c98d06a))

### Features

- Added semver auto increment
  ([`6791697`](https://github.com/KataCards/cardarena-remote-stage/commit/67916978ac1297c4385e0a079a49c7783dd1447f))

* feat: added semver auto increment

* fix: js into mjs


## v0.1.0 (2026-04-14)

### Bug Fixes

- Added more advanced fullscreen logic for testing purposes
  ([`e1f30a0`](https://github.com/KataCards/cardarena-remote-stage/commit/e1f30a0992e6b96f573389a25f0e381138713b74))

- Added Returntype to main.py L22, Created shared util parse_comma_seperated for Config.py(App +
  Security), Removed dead Config Option Error_page, Added Type to Build_liefspan.
  ([`0319889`](https://github.com/KataCards/cardarena-remote-stage/commit/0319889629312bc019d36bf209953fc600ef6d32))

- Added wildcard to gitignore
  ([`a24e5d6`](https://github.com/KataCards/cardarena-remote-stage/commit/a24e5d6846bb758aea957d87a6e021d3e5b4f78d))

- Finished claning up
  ([`8339fff`](https://github.com/KataCards/cardarena-remote-stage/commit/8339fffbdabf5d2ce9ce3e3a84e308b1f7cf9dde))

- Fixed Failing Tests due to logic changes
  ([`c35f068`](https://github.com/KataCards/cardarena-remote-stage/commit/c35f0689e873ce2d042cedb026ca9b86d0f800fb))

- Fixed Issue where lru_chache of Settings was breaking a test and not improving speed as needed.
  ([`65b337d`](https://github.com/KataCards/cardarena-remote-stage/commit/65b337d017080853de8e977039b68660b1ac569b))

- Fixed multiple smaller issues and added new util function
  ([`9ffbf7b`](https://github.com/KataCards/cardarena-remote-stage/commit/9ffbf7b388c44b427a1169df6e339878f1a770aa))

- Fixed silent error in schedule.py, fixed minor issues like types.
  ([`e847f14`](https://github.com/KataCards/cardarena-remote-stage/commit/e847f14ca3f795fcc1d5e85f398a721d71761a35))

- Fixed smaller severitry bugs.
  ([`9b056aa`](https://github.com/KataCards/cardarena-remote-stage/commit/9b056aa90dc72e725f0e49cf8ecef4ce3192bc2d))

- Fixed that the kiosk overwrote the engines launch args.
  ([`8b5edeb`](https://github.com/KataCards/cardarena-remote-stage/commit/8b5edeb43da84aed7e0536383261b157c73da27d))

- Fixed the issues ContextLeaking, Ineffective Logging, Ad Break Event Timing, Successtracking,
  Exceptionhandler, Optional API-Key secret
  ([`2ddcc06`](https://github.com/KataCards/cardarena-remote-stage/commit/2ddcc06923feea1e17dca7423148c1777e59b3c8))

- Harded lazy code, added checks fixed circular import
  ([`ffc0d22`](https://github.com/KataCards/cardarena-remote-stage/commit/ffc0d22e266d01c0efe3fb8aa56ddfb3466a74d2))

- I didnt error read readme.md my bad
  ([`e416b43`](https://github.com/KataCards/cardarena-remote-stage/commit/e416b4377751d000e08337e41871d7e5de54f4d9))

- Ignore sub-frame document errors in response handler
  ([`4f97b9d`](https://github.com/KataCards/cardarena-remote-stage/commit/4f97b9d3ce8db02b6c46381651b24b26e2fb72f1))

YouTube (and other sites) load iframes whose sub-frame document requests return 403. The previous
  guard only checked resource_type == "document" which passes for both main-frame and iframe
  responses, causing the kiosk to navigate to the error page even when the main page loaded fine.

Add response.frame != page.main_frame guard so only the top-level navigation's response code
  triggers error page routing.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Improved on the pointed out issues like concurrency, waiting and so on.
  ([`c4176a9`](https://github.com/KataCards/cardarena-remote-stage/commit/c4176a968f58a6cceba93b2ca4815ec992fe394c))

- Only wire on_error when error_map is non-empty
  ([`4ac733b`](https://github.com/KataCards/cardarena-remote-stage/commit/4ac733bb9fbebb725922e37009f6340dbce6e933))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Pushed local db to github. whoops
  ([`9927d1a`](https://github.com/KataCards/cardarena-remote-stage/commit/9927d1a7334c797099d40f6acdf2e4749d43aed8))

- Remove dead border-top:none, add cascade order comment on orientation queries
  ([`2c5c7c8`](https://github.com/KataCards/cardarena-remote-stage/commit/2c5c7c8f845efbbe7a7812df7e9aff3cc3b9d51e))

- Remove duplicate overflow:hidden in main rule
  ([`7aaba25`](https://github.com/KataCards/cardarena-remote-stage/commit/7aaba25021600245825caa01d729d82ed8045904))

- Remove redundant height:100dvh from body (already set in shared html,body block)
  ([`cb2a1f7`](https://github.com/KataCards/cardarena-remote-stage/commit/cb2a1f7bb1bd97af658ff6a76b9fa89a892b519e))

- Remove redundant overflow-x:hidden from body (overflow:hidden covers both axes)
  ([`43872db`](https://github.com/KataCards/cardarena-remote-stage/commit/43872dbccce6ec2ea1ce731ea0170f9e4a70a708))

- Rewritten Tests that relied on dead code
  ([`f462fcd`](https://github.com/KataCards/cardarena-remote-stage/commit/f462fcd7be69ded9bcf3383a5b272e93b4936034))

- Shortend komment to only neccesairy lenght
  ([`1972819`](https://github.com/KataCards/cardarena-remote-stage/commit/19728197cefd2ff0bf5e274d868fe121cd4d4b0e))

- **api**: Accurate ValidationError comment, tighten frozen test assertions
  ([`debe7d7`](https://github.com/KataCards/cardarena-remote-stage/commit/debe7d7de394eae0ace3f5deb645d8cf65dbaf45))

- **api**: Narrow exception catch to RuntimeError in kiosk routes
  ([`1de9c1c`](https://github.com/KataCards/cardarena-remote-stage/commit/1de9c1c72e55ac0d2cee755ca6e522375b3d0bca))

- **api**: Scheduler CancelledError, None guards, task cleanup
  ([`ffbdac6`](https://github.com/KataCards/cardarena-remote-stage/commit/ffbdac6adf179b6ffbd81bd0540957f9afab441c))

- **tests**: Update playwright engine tests for document-only response filter
  ([`af4004b`](https://github.com/KataCards/cardarena-remote-stage/commit/af4004b26d17dcb8a126d56e2b47234aeab679ec))

- Rename test to reflect on_error is called directly (not via handle_error) - Add resource_type =
  "document" to existing response test fixtures - Add test covering sub-resource types (image,
  stylesheet, script, font, xhr) are ignored - Fix ConcreteKiosk stub missing go_home abstract
  method

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Chores

- Remove stale test_config.py (src.api.config no longer exists)
  ([`a54c32b`](https://github.com/KataCards/cardarena-remote-stage/commit/a54c32b97e80c173e4c6998793e12e68a640404a))

### Code Style

- Clarify pre-emptive margin reset on .page-header .status
  ([`29eb0d2`](https://github.com/KataCards/cardarena-remote-stage/commit/29eb0d29140ab299a3c185388061db8070d69c90))

### Features

- Add abstract KioskFactory base class
  ([`ca314b4`](https://github.com/KataCards/cardarena-remote-stage/commit/ca314b4819d1ddf707ddcd7043e553169754587a))

- Add kiosk_error_routing setting (default true)
  ([`c16ced3`](https://github.com/KataCards/cardarena-remote-stage/commit/c16ced306c8c69f9adbe541d96301db5061b9bda))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Add KioskStartupService
  ([`e5af43d`](https://github.com/KataCards/cardarena-remote-stage/commit/e5af43d1fdc16e87d103bc42f40535221ded1ab0))

- Add landscape/portrait orientation media queries to template
  ([`2ffcd5d`](https://github.com/KataCards/cardarena-remote-stage/commit/2ffcd5d3bd17d4585d1589c0ebc5d4929df47552))

- Add no-scroll foundation to resource page template
  ([`e62dab9`](https://github.com/KataCards/cardarena-remote-stage/commit/e62dab90c9f4162300b93fedc1d06a743fca9eaf))

- Add page-header flex row component to template
  ([`e87a540`](https://github.com/KataCards/cardarena-remote-stage/commit/e87a5403e5e5a6ae136c0cbe3307eca1791127e4))

- Add page-header to all error pages
  ([`05a5845`](https://github.com/KataCards/cardarena-remote-stage/commit/05a584521078d7f00297a1ed6a4e4de0257f51ac))

- Add page-header to boot-ready page
  ([`b88a107`](https://github.com/KataCards/cardarena-remote-stage/commit/b88a10777a9290e5ef94cbff89d720bd4caf7f79))

- Add PlaywrightKioskFactory
  ([`96cfd53`](https://github.com/KataCards/cardarena-remote-stage/commit/96cfd535371bfca30d7e00273d5819ca7780fd2f))

- Added first blueprints and components
  ([`7501aab`](https://github.com/KataCards/cardarena-remote-stage/commit/7501aab5de389d82a5849e2cb99c6157ef304cde))

- Added fixes for oversights in the baseclases, added playwright engine and controls, added
  decorator to save lines because of repetition.
  ([`29d3ff5`](https://github.com/KataCards/cardarena-remote-stage/commit/29d3ff531147fc0981ca578e573946a9a6efa64c))

- Added Ip-Based Auth as a alternative, fixed smaller issues with caused by the FastAPI limitations.
  ([`bdf54d6`](https://github.com/KataCards/cardarena-remote-stage/commit/bdf54d63da6819c1168eca4b5f200fd9e19486d9))

- Added launch args, added go_home, fixed a bug and added a kiosk demo
  ([`152cc99`](https://github.com/KataCards/cardarena-remote-stage/commit/152cc997e4dd64820f65d718f90ebe2d8d7bdf58))

- Added minimal demo., fix: removed go_home from control base class since this can be orchestrated
  by the kiosk.
  ([`d9e825b`](https://github.com/KataCards/cardarena-remote-stage/commit/d9e825bb4d7d9f975d92a717a64c9b7b233074a4))

- Added Playwright Kiosk
  ([`315992a`](https://github.com/KataCards/cardarena-remote-stage/commit/315992ad41bc409db4f5405c0b27c2dca158e55e))

- Added scaffold pages for basic testing
  ([`80c1c8e`](https://github.com/KataCards/cardarena-remote-stage/commit/80c1c8eff0734da15d7ca23ad4e851577b2c28d2))

- Added security abstraction layer
  ([`0e47fb7`](https://github.com/KataCards/cardarena-remote-stage/commit/0e47fb7b47a3176fa8318907052533de70578b38))

- Added uvlock file
  ([`8d0d649`](https://github.com/KataCards/cardarena-remote-stage/commit/8d0d64921ec5cb711a5095c16001793907962d4b))

- Api_key provider implementation v1.
  ([`2764130`](https://github.com/KataCards/cardarena-remote-stage/commit/2764130c8c0a44e90ec586ae6eec7eeede01c702))

- Better .env controls
  ([`139a8a4`](https://github.com/KataCards/cardarena-remote-stage/commit/139a8a4082af8ee25ef3c4b6e06b788722552ae1))

- Fixed Ruff errors and added a missing build step
  ([`0a69990`](https://github.com/KataCards/cardarena-remote-stage/commit/0a69990a4136751408f8f42f42bd89349ce10469))

- Frist fully implemented functioning version
  ([`cb68b78`](https://github.com/KataCards/cardarena-remote-stage/commit/cb68b78eb8b748ea7e8b64f9d23b645744f92981))

- Reenforced some code, added pipeline
  ([`c6821bc`](https://github.com/KataCards/cardarena-remote-stage/commit/c6821bc634468748ec507f3f271955806fb6e7d7))

- Security provider + api layer version 0.5, needs proper evaluation once I got time
  ([`06ef271`](https://github.com/KataCards/cardarena-remote-stage/commit/06ef271cd189297a8edc2ca89c93369bed22405f))

- Skip error map when kiosk_error_routing is false
  ([`77dcf92`](https://github.com/KataCards/cardarena-remote-stage/commit/77dcf9258334101493edcf391a6aadf36ba98dc6))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- Tighten font sizes for no-scroll kiosk viewports
  ([`1387aa6`](https://github.com/KataCards/cardarena-remote-stage/commit/1387aa6a270cb3a4c700be249ceb06f7dfbc6e8c))

- Updated .env.example
  ([`20316c6`](https://github.com/KataCards/cardarena-remote-stage/commit/20316c6e2622fc44f87c91c2750419bca314b664))

- **api**: Control routes (navigate, reload)
  ([`c6ed72a`](https://github.com/KataCards/cardarena-remote-stage/commit/c6ed72a9108352fb7ab4c58984565a91ff516f2e))

- **api**: Health, kiosk routes, and app composition root
  ([`f582870`](https://github.com/KataCards/cardarena-remote-stage/commit/f58287015230d0f40ca24f25ab86c7d9f57c3f39))

Implements GET /health (no auth) and GET /kiosks, GET /kiosks/{uuid} (READ scope) via
  factory-pattern routers, plus the FastAPI composition root that defers kiosk construction to
  lifespan to avoid import-time env validation failures.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **api**: Kioskregistry and ApiSettings
  ([`bf13a82`](https://github.com/KataCards/cardarena-remote-stage/commit/bf13a82bd2156fd74a24adbb20543863beb38400))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **api**: Pydantic models for kiosk and schedule
  ([`3ca31b3`](https://github.com/KataCards/cardarena-remote-stage/commit/3ca31b3a972f53b7a4573690f764351df4dfc7d9))

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

- **api**: Scheduler and schedule/ad-break routes
  ([`053132c`](https://github.com/KataCards/cardarena-remote-stage/commit/053132c094bb59a6c7a20fc8258dab8b65a4e65e))

Implements KioskScheduler with per-kiosk asyncio task management and schedule/cancel/ad-break
  routes, wired into app.py.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Refactoring

- Replace lifespan in main.py with KioskStartupService
  ([`8220802`](https://github.com/KataCards/cardarena-remote-stage/commit/82208021a0d5c69f395d3ed576921135fb784df5))

### Testing

- **api**: Add get_settings cache test
  ([`ffba730`](https://github.com/KataCards/cardarena-remote-stage/commit/ffba7304f59a2d46f4adf6ebb8466f246e5fdc89))

- **api**: Tighten control route test assertions
  ([`9b13ff4`](https://github.com/KataCards/cardarena-remote-stage/commit/9b13ff45ee3226c0b9304f18c077f520a7dafc70))
