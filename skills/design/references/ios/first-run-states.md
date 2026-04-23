---
name: first-run-states
description: iOS first-run + edge states (launch, onboarding, permissions, sign-in, empty/error/loading, paywalls)
platform: ios
---

# iOS first-run and edge-state reference (iOS 18 & iOS 26)

A practical, Apple-sourced reference for launch screens, onboarding, permissions, sign-in, empty/error/loading states, and paywalls. Targets **iOS 18** and **iOS 26** (Liquid Glass, WWDC25). Every section calls out version-gated APIs, verbatim guidelines where they matter, and explicit do/don't pairs.

---

## 1. Launch screens

### 1.1 What a launch screen is for

Per HIG → *Launching*: **"The ideal launch screen is effectively invisible to people, because it simply provides a context for your initial content."** The launch screen's sole job is to provide **visual continuity** between the moment the user taps the icon and the moment the first screen is interactive. It is not a splash screen, a branding opportunity, or an "About" window.

The defining rule is **structural identity with the first screen**: the launch screen should look like the first screen with its data removed. When it's replaced, users should perceive no transition — no flash, no reveal, no animation.

### 1.2 What's allowed vs banned

| Allowed | Banned |
|---|---|
| Solid background matching the first screen | Text of any kind (cannot be localized) |
| A structural skeleton: nav bar, tab bar, toolbar | Logos or branding not present on the first screen |
| An image that is a fixed part of the first screen | Loading spinners or progress bars |
| System-provided materials (auto-adapts to Dark Mode) | Ads, marketing, copyright, "About" info |
| A single solid color for games that open to one | Artistic expression or "splash" treatments |
| Dark Mode / Light Mode variants via asset catalog | Artificial delays to make the launch screen visible |

App Store Review cross-references: **Guideline 2.3.3** prohibits using launch/splash art as App Store screenshots, and **Guideline 4.2** flags apps that are "primarily marketing materials." An artificially long launch screen can trigger rejection.

### 1.3 Two implementation approaches

**Storyboard approach** — `LaunchScreen.storyboard`, set via `UILaunchStoryboardName`. Supported since iOS 8; still valid. Use Auto Layout so it adapts to all sizes and orientations. Best when your first screen has a complex structural layout that the plist dictionary can't express.

**Info.plist dictionary approach (preferred for iOS 14+/SwiftUI)** — the `UILaunchScreen` dictionary describes the screen declaratively. All keys:

| Key | Type | Purpose |
|---|---|---|
| `UIColorName` | String | Asset-catalog color name (defaults to `systemBackground`) |
| `UIImageName` | String | Asset-catalog image, centered |
| `UIImageRespectsSafeAreaInsets` | Boolean | Keep image inside safe area |
| `UINavigationBar` | Dictionary | Show a nav bar; optionally set `UIImageName` |
| `UITabBar` | Dictionary | Show a tab bar; optionally set `UIImageName` |
| `UIToolbar` | Dictionary | Show a toolbar; optionally set `UIImageName` |

Minimal example:

```xml
<key>UILaunchScreen</key>
<dict>
    <key>UIColorName</key>
    <string>LaunchBackground</string>
    <key>UIImageName</key>
    <string>LaunchLogo</string>
    <key>UIImageRespectsSafeAreaInsets</key>
    <true/>
</dict>
```

Structural skeleton example (mirrors a tab-bar/nav-bar app):

```xml
<key>UILaunchScreen</key>
<dict>
    <key>UIColorName</key>
    <string>LaunchBackground</string>
    <key>UINavigationBar</key>
    <dict/>
    <key>UITabBar</key>
    <dict/>
</dict>
```

**Per-URL-scheme variants** — the plural `UILaunchScreens` dictionary lets deep links show a different skeleton matching their destination via `UILaunchScreenDefinitions` and `UIURLToLaunchScreenAssociations`. Useful when `myapp://edit` should land on a screen without a tab bar, for example.

### 1.4 iOS 26 / Liquid Glass considerations

**No new `UILaunchScreen` keys.** The dictionary schema is unchanged in iOS 26. Key implications:

- When you recompile with Xcode 26 targeting iOS 26, any `UINavigationBar` / `UITabBar` / `UIToolbar` declared in the launch dictionary **renders with Liquid Glass material automatically** — no code changes required. This preserves seamless continuity as long as the app itself has adopted the new design.
- Liquid Glass is "best reserved for the navigation layer that floats above the content" (WWDC25 session 219, *Meet Liquid Glass*). Keep your launch screen's content layer opaque and let the system handle the bar chrome.
- Don't try to paint Liquid Glass manually via a static image. The material is rendered dynamically; a baked-in screenshot will look wrong against user wallpaper and in dark mode.
- iOS 26 itself displays a short system-level Liquid Glass intro video on first launch after the OS update. You don't trigger this; don't replicate it.
- Use asset-catalog colors/images with Light/Dark variants. Respect Reduce Transparency and Increased Contrast (handled automatically by system materials).

### 1.5 Anti-patterns

**Don't** show a centered logo over a branded gradient for 2 seconds. **Don't** include your version number or copyright. **Don't** add a "Loading…" label or spinner. **Don't** introduce an artificial delay so users can read a tagline. **Don't** submit the launch image as an App Store screenshot — that's a direct 2.3.3 rejection.

---

## 2. First-run onboarding

### 2.1 Apple's five principles (HIG → Onboarding)

1. **Provide onboarding that helps people enjoy your app, not just set it up.** "Avoid including setup or licensing details."
2. **Get to the action quickly.** "Let people dive right in. If you need to provide tutorials or intro sequences, **give people a way to skip them and don't automatically show them when people return.**"
3. **Anticipate the need for help.** Teach in context, when the user is near a stuck point — not upfront.
4. **Stick to the essentials in tutorials.** "Education isn't a substitute for great app design. **If people seem to need too much guidance, revisit the design of your app.**"
5. **Make learning fun and discoverable.** "Learning by doing is a lot more fun and effective than reading a list of instructions. Avoid displaying static screenshots that appear interactive."

### 2.2 When onboarding is warranted

| Favors onboarding | Against onboarding |
|---|---|
| App needs personal context to produce useful content (health profile, goals) | App is immediately useful with zero configuration |
| Requires a sign-in or meaningful permissions to function | Works locally without accounts |
| Introduces a genuinely novel interaction with no mental model | Follows standard HIG patterns (tab bar, list-detail) |
| Game with an unfamiliar core loop | Utility whose purpose is obvious from the first screen |

### 2.3 Should I show onboarding? Decision tree

```
                ┌──────────────────────────────────┐
                │ Does the first screen produce    │
                │ value with ZERO user input?      │
                └────────────┬─────────────────────┘
                             │
              ┌──────YES─────┴─────NO──────┐
              ▼                             ▼
      NO ONBOARDING               ┌──────────────────────────────┐
      (open to content)           │ Can we derive needed info    │
                                  │ from device/Apple ID/iCloud/ │
                                  │ HealthKit/Sign in with Apple?│
                                  └──────────┬───────────────────┘
                                             │
                                ┌─────YES────┴────NO──────┐
                                ▼                          ▼
                         USE DEFAULTS          ┌──────────────────────┐
                         NO ONBOARDING         │ Is the missing info  │
                                               │ a permission or a    │
                                               │ deeply personal goal?│
                                               └──────────┬───────────┘
                                                          │
                                         ┌────YES─────────┴──────NO──┐
                                         ▼                            ▼
                               MINIMAL ESSENTIAL SETUP       TEACH IN CONTEXT
                               (1–3 steps, skippable,        (tooltips, first-
                               request permissions in        time hints at point
                               context, not upfront)         of use — no upfront
                                                             carousel)
```

**Always** provide Skip, **never** re-show on subsequent launches, and **always** let users replay tutorials from Settings.

### 2.4 Apple's own apps as reference

**Onboard:** Health (profile + permissions), Fitness (move/exercise/stand goals), Journal (novel concept, on-device privacy explanation), Sleep, Screen Time. Personalization-heavy apps (Music, Podcasts, News, TV) do a brief, skippable "tell us what you like" step.

**Don't onboard:** Notes, Reminders, Mail, Messages, Calendar, Safari, Clock, Calculator, Weather, Maps, Photos. The metaphor is instantly recognizable, and the first screen is useful immediately.

The pattern: **Apple onboards only when personalization is required, when meaningful permissions are needed, or when a genuinely novel concept must be introduced.** If your app fits a familiar metaphor, don't onboard.

### 2.5 Walkthroughs, welcome screens, and "What's New"

Heavyweight walkthroughs are a red flag per HIG — they imply the UI can't stand on its own. Prefer in-context, just-in-time teaching. Welcome screens are tolerated when they're short (1–3 steps), request only necessary data, and hand users off to an immediately usable first screen.

For post-update "What's New" surfaces: short, dismissable, in-context hints are better than blocking modals. When you must use a modal, follow Apple's pattern (Photos/Messages/Maps after major updates): one sheet, 3–5 feature cards, a prominent Continue button, and don't re-show on subsequent launches. Never use "What's New" as upsell.

### 2.6 Anti-patterns

**Forced onboarding** (no Skip), **upfront permission walls** before showing any value, **static annotated screenshots** that pretend to be interactive, **licensing/copyright slides** inside onboarding, **re-showing onboarding on every launch**, and **"What's New" as marketing** are all HIG violations and friction-generating anti-patterns.

---

## 3. Permission requests — general principles

### 3.1 Timing: in-context, not upfront

HIG → *Requesting Permission*: **"Request personal data only when your app clearly needs it."** Ask only when the user uses the feature that needs the data. Request at launch only when the app cannot function without it — e.g., an AR app requesting camera access on the first screen is acceptable because the user's context makes the need self-evident.

### 3.2 The pre-permission priming pattern

**Why it exists:** once a user taps "Don't Allow," iOS will not re-show the system dialog. Recovery requires a Settings deep link and user effort. Because the first ask is effectively terminal, you should warm the user up with your own explainer **before** invoking the system API.

**Correct flow:**

1. Show a custom in-app explainer with a clear benefit statement and **Continue / Not now** buttons.
2. Only when the user taps Continue, call the native API (`AVCaptureDevice.requestAccess`, `CLLocationManager.requestWhenInUseAuthorization`, etc.).
3. On denial, degrade gracefully and offer an **Open Settings** button using `UIApplication.openSettingsURLString`.

HIG caution: your custom explainer must **not impersonate** the system alert. "Use the system-provided alert… avoid adding custom prompts that replicate the standard alert's behavior or appearance."

```swift
struct PrePermissionView: View {
    let onContinue: () -> Void
    let onCancel: () -> Void
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "camera.fill").font(.largeTitle)
            Text("Scan QR codes").font(.title2).bold()
            Text("We'll ask for camera access next so you can scan codes at the venue.")
                .multilineTextAlignment(.center)
            Button("Continue", action: onContinue).buttonStyle(.borderedProminent)
            Button("Not now", action: onCancel)
        }
        .padding()
    }
}
```

```swift
import AVFoundation
import UIKit

func ensureCameraAccess() async -> Bool {
    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized:    return true
    case .notDetermined: return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        await MainActor.run { openAppSettings() }
        return false
    @unknown default: return false
    }
}

@MainActor
func openAppSettings() {
    if let url = URL(string: UIApplication.openSettingsURLString) {
        UIApplication.shared.open(url)
    }
}
```

### 3.3 Purpose strings

Purpose strings (Info.plist `NS*UsageDescription` keys) must be **specific**, one sentence, sentence case, include an **example** of use, never include the app's name, and must be **localized** via `InfoPlist.strings`. App Store Review's most common privacy rejection (5.1.1) is a generic purpose string.

**Good vs bad:**

| Permission | Bad | Good |
|---|---|---|
| Camera | "Access to camera." | "Allows scanning QR codes to check in at a venue." |
| Location (when-in-use) | "We need your location." | "Shows restaurants near you and calculates delivery times." |
| Photos | "We need photos." | "Lets you pick a profile picture from your library." |
| Contacts | "We use your contacts." | "Finds friends already using the app so you can message them." |
| Tracking (ATT) | "For ads." | "Your data will be used to show ads tailored to your interests across other companies' apps and websites. Example: we share a device identifier with ad partners." |

### 3.4 Handling denial

**Never block the app** on denied permissions — Guideline 5.1.1(iv) prohibits manipulation, trickery, or force. Degrade to a non-personalized feature path, offer a clear "Open Settings" button, and explain what the user gains by enabling.

---

## 4. Per-permission best practices

### 4.1 Location (CoreLocation)

**Info.plist keys:** `NSLocationWhenInUseUsageDescription`, `NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationTemporaryUsageDescriptionDictionary`.

**Authorization:** `.notDetermined`, `.restricted`, `.denied`, `.authorizedWhenInUse`, `.authorizedAlways`. **Accuracy (iOS 14+):** `.fullAccuracy` vs `.reducedAccuracy` (~20 km radius, positions up to ~20 minutes stale; beacon/region monitoring disabled in reduced mode).

**Escalation rule (Apple-recommended):** always request `.authorizedWhenInUse` first. Only after the user has seen foreground value should you call `requestAlwaysAuthorization()`, which triggers a one-time upgrade dialog. After denial, the system will not re-prompt.

**Temporary precise location (iOS 14+):** if granted approximate, ask for a one-time precise upgrade for a specific task:

```swift
manager.requestTemporaryFullAccuracyAuthorization(withPurposeKey: "WantsToNavigate")
```

Each purpose key must exist in `NSLocationTemporaryUsageDescriptionDictionary`. Precise mode lasts until relaunch.

```swift
import CoreLocation

final class LocationController: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func requestWhenInUse() {
        if manager.authorizationStatus == .notDetermined {
            manager.requestWhenInUseAuthorization()
        }
    }

    func escalateToAlways() {
        if manager.authorizationStatus == .authorizedWhenInUse {
            manager.requestAlwaysAuthorization()
        }
    }

    func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        switch m.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways: m.startUpdatingLocation()
        case .denied, .restricted: /* graceful UI + Settings deep link */ break
        default: break
        }
    }

    func locationManager(_ m: CLLocationManager, didUpdateLocations locs: [CLLocation]) { }
}
```

**Indicator:** status bar arrow — solid when currently accessing, hollow when recent/geofence only.

**Anti-patterns:** asking for Always before demonstrating When-In-Use value; not handling reduced accuracy; blocking the feature entirely when denied instead of degrading.

### 4.2 Photos (PhotoKit / PhotosUI)

Three access patterns ordered by preference:

**(1) `PhotosPicker` / `PHPickerViewController` — preferred.** No permission required; runs out-of-process; only the user's selections return to your app. Do not add `NSPhotoLibraryUsageDescription` if this is your only photo surface.

```swift
import PhotosUI
import SwiftUI

struct PickerExample: View {
    @State private var selection: PhotosPickerItem?
    @State private var image: Image?
    var body: some View {
        PhotosPicker("Choose photo", selection: $selection, matching: .images)
            .onChange(of: selection) { _, new in
                Task {
                    if let data = try? await new?.loadTransferable(type: Data.self),
                       let ui = UIImage(data: data) {
                        image = Image(uiImage: ui)
                    }
                }
            }
        image?.resizable().scaledToFit()
    }
}
```

**(2) `PHPhotoLibrary` direct access** — only for Photos-like apps that enumerate assets, metadata, albums. Users may grant **`.limited`** (iOS 14+), exposing only the photos they picked. Let users update that selection with `PHPhotoLibrary.shared().presentLimitedLibraryPicker(from:)`. Suppress the repeating system prompt by setting `PHPhotoLibraryPreventAutomaticLimitedAccessAlert = YES` in Info.plist.

**(3) `UIImagePickerController`** — legacy; avoid for new work.

**Info.plist:** `NSPhotoLibraryUsageDescription` for reads; **`NSPhotoLibraryAddUsageDescription`** for write-only (less intrusive prompt).

### 4.3 Contacts — iOS 18 limited access (critical)

**iOS 18 introduced a two-stage contacts prompt** mirroring the Photos model: "Allow access to contacts?" → if Continue, "Select Contacts… / Allow Full Access." A new `.limited` state (`CNAuthorizationStatus`) joins `.notDetermined`, `.denied`, `.restricted`, `.authorized`. Under `.limited`, the app reads only contacts the user explicitly shared; writes/creates are still permitted.

Apple introduced two preferred APIs in iOS 18. **Prefer `ContactAccessButton`** for search-driven flows — it yields the highest grant rates and best satisfies data-minimization rules under Guideline 5.1.1.

```swift
import SwiftUI
import Contacts
import ContactsUI

struct ContactSearchView: View {
    @Binding var searchText: String
    @State var authorizationStatus: CNAuthorizationStatus = .notDetermined

    var body: some View {
        List {
            ForEach(searchResults(for: searchText)) { person in
                ResultRow(person)
            }
            if authorizationStatus == .limited || authorizationStatus == .notDetermined {
                ContactAccessButton(queryString: searchText) { identifiers in
                    let contacts = await fetchContacts(withIdentifiers: identifiers)
                    dismissSearch(withResult: contacts)
                }
                .contactAccessButtonCaption(.phone)
            }
        }
    }
}
```

`ContactAccessButton` is rendered in a separate process; it must be **legible and unobscured** or taps are silently rejected. For bulk-add flows, use `.contactAccessPicker(isPresented:completionHandler:)`.

**Escalation quirk:** once in `.limited`, calling `requestAccess` again does **not** re-open the full-access sheet. To escalate, deep-link to Settings.

**Which API to use:**

| API | Works when | Use for |
|---|---|---|
| `CNContactPickerViewController` | Any status; always full DB | One-off ephemeral picks (one email/phone) |
| `CNContactStore` | `.authorized` or `.limited` | Main read/write store |
| `ContactAccessButton` | `.limited` or `.notDetermined` | Search-driven incremental access (best UX) |
| `contactAccessPicker` | `.limited` only | Bulk-add to the permitted set |

Reference: WWDC24 session 10121, *Meet the Contact Access Button*.

### 4.4 Camera

`NSCameraUsageDescription` required (crash otherwise). Request with `AVCaptureDevice.requestAccess(for: .video)`. Status bar shows a **green dot** whenever the camera is active; it cannot be suppressed.

### 4.5 Microphone

`NSMicrophoneUsageDescription` required. iOS 17+: prefer `AVAudioApplication.requestRecordPermission`. Pre-iOS 17 / deprecated: `AVAudioSession.sharedInstance().requestRecordPermission`.

```swift
import AVFAudio
if #available(iOS 17, *) {
    AVAudioApplication.requestRecordPermission { granted in /* ... */ }
} else {
    AVAudioSession.sharedInstance().requestRecordPermission { granted in /* ... */ }
}
```

Status bar shows an **orange dot** while active.

### 4.6 Notifications

No Info.plist key required (push needs the Push Notifications entitlement; critical alerts require a separate Apple-approved entitlement).

**Preferred pattern:** start with `.provisional` authorization — delivered **quietly** to Notification Center with no permission prompt. The first time a user sees one, iOS offers inline "Keep Quietly / Turn Off / Deliver Prominently" choices. Only escalate to full authorization after the user has engaged with the feature.

```swift
import UserNotifications
let center = UNUserNotificationCenter.current()
let settings = await center.notificationSettings()
if settings.authorizationStatus == .notDetermined {
    try await center.requestAuthorization(options: [.alert, .sound, .badge, .provisional])
}
```

**Interruption levels (iOS 15+):** `.passive` (list only, no wake), `.active` (default), `.timeSensitive` (pierces Focus; requires entitlement), `.critical` (pierces mute + Focus; special Apple-approved entitlement). Set `relevanceScore` (0.0–1.0) so iOS ranks notifications in the daily Summary.

**Anti-patterns:** requesting full authorization at first launch without context (40–60% typical denial rates); ignoring provisional; gating app use on notification permission.

### 4.7 App Tracking Transparency

`NSUserTrackingUsageDescription` required; without it, the system will not prompt and the app may be rejected.

**When ATT is required:** tracking user activity across apps and websites owned by **other companies** for advertising/measurement, sharing device data with **data brokers**, or using IDFA (which returns zeros without authorization). Cross-app analytics within apps you own, using IDFV, does not require ATT (and must not be combined with third-party data).

**Implementation must run when app is active:**

```swift
import AppTrackingTransparency
import AdSupport

@MainActor
func requestTracking() async {
    let status = await ATTrackingManager.requestTrackingAuthorization()
    if status == .authorized {
        _ = ASIdentifierManager.shared().advertisingIdentifier
    }
}
```

If called too early (cold launch before UI is active) the prompt silently fails and status returns `.notDetermined`. **Denial is terminal** — you cannot re-prompt; you can only deep-link to Settings. Always pre-prime with a custom explainer.

**Guideline 5.1.2 rules:** you must clearly disclose third-party data sharing (as of **November 2025**, including **third-party AI services**) and obtain explicit permission. You may not **incentivize** permission (no rewards, discounts, paywalls) and may not **withhold content or functionality** from users who deny. Generic purpose strings are a common rejection — include a concrete example.

---

## 5. Sign-in

### 5.1 Guideline 4.8 — when Sign in with Apple (or equivalent) is required

Current text (last updated Feb 6, 2026): **"Apps that use a third-party or social login service (such as Facebook Login, Google Sign-In, Sign in with Twitter, Sign In with LinkedIn, Login with Amazon, or WeChat Login) to set up or authenticate the user's primary account with the app must also offer as an equivalent option another login service"** that limits collection to name + email, supports private email relay, and does not collect in-app interactions for advertising without consent.

Sign in with Apple satisfies all three criteria, and App Review still cites it explicitly in rejections (*"Guideline 4.8 – Design – Sign in with Apple"*).

**Exceptions** (no equivalent service required): apps using only their own account system, alternative marketplaces with marketplace-specific login, education/enterprise accounts, government eID, and pure third-party clients (e.g., a Dropbox client).

**Prominence parity:** the alternate login must be offered on the same screen, at equivalent size and prominence, with equivalent data minimization.

### 5.2 HIG position on sign-in

HIG → *Managing accounts*: **"Delay sign-in for as long as possible."** "People often abandon apps when they're forced to sign in before they can do anything useful." A shopping app should let people browse; only require sign-in at checkout. Examples to follow:

- **Explain the benefits** of creating an account on the sign-in screen.
- **Prefer Sign in with Apple**; otherwise prefer **passkeys**.
- **Use Password AutoFill and SMS one-time-code filling** when you retain passwords.
- **Identify the authentication method explicitly** — "Sign In with Face ID," not just "Sign In."
- **Avoid in-app biometric toggles** — biometrics are a system-level setting.
- **Don't call your password a "passcode"** — that term is reserved for the device passcode.

### 5.3 Continue as guest

Guest mode is explicitly supported by HIG ("let people enjoy your app or game without an account when your core functionality doesn't require it") and fits Guideline 5.1.1(v) ("If your app doesn't include significant account-based features, let people use it without a login"). If you auto-create guest accounts server-side, they must also be deletable under 5.1.1(v).

### 5.4 Sign in with Apple implementation

**Framework:** AuthenticationServices. **Button styles** (`ASAuthorizationAppleIDButton.Style`): `.black`, `.white`, `.whiteOutline`. **Button types**: `.signIn`, `.signUp` (iOS 13.2+), `.continue`, `.default`. Use the system-provided button; if you build a custom one, title font size = 43% of button height, capitalize only "Sign"/"Continue" and "Apple."

**Nonce handling** (mitigates replay): generate a raw random nonce per request, send `SHA-256(raw)` as `request.nonce`, persist the raw value client-side, and verify on the server that the returned identity token's `nonce` claim equals `SHA-256(raw)`.

```swift
import SwiftUI
import AuthenticationServices

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var isSignedIn = false
    var currentNonce: String?

    func restoreSession() {
        guard let userID = KeychainHelper.read(key: "appleUserID") else { return }
        ASAuthorizationAppleIDProvider().getCredentialState(forUserID: userID) { state, _ in
            DispatchQueue.main.async {
                switch state {
                case .authorized:                         self.isSignedIn = true
                case .revoked, .notFound, .transferred:   self.signOutLocally()
                @unknown default:                         self.signOutLocally()
                }
            }
        }
    }

    func handle(_ result: Result<ASAuthorization, Error>) {
        guard case .success(let auth) = result,
              let credential = auth.credential as? ASAuthorizationAppleIDCredential,
              let nonce = currentNonce,
              let idTokenData = credential.identityToken,
              let idToken = String(data: idTokenData, encoding: .utf8)
        else { return }

        KeychainHelper.save(key: "appleUserID", value: credential.user)
        // POST idToken + authCode + raw nonce to your server.
        // Server verifies signature/issuer/audience + nonce, stores the refresh token
        // so account deletion can later call /auth/revoke.
        isSignedIn = true
    }

    func signOutLocally() {
        isSignedIn = false
        KeychainHelper.delete(key: "appleUserID")
    }
}

struct SignInView: View {
    @StateObject var vm = AuthViewModel()
    @Environment(\.colorScheme) var scheme

    var body: some View {
        VStack(spacing: 16) {
            SignInWithAppleButton(.signIn) { request in
                let raw = CryptoUtils.randomNonceString()
                vm.currentNonce = raw
                request.requestedScopes = [.fullName, .email]
                request.nonce = CryptoUtils.sha256(raw)
            } onCompletion: { vm.handle($0) }
            .signInWithAppleButtonStyle(scheme == .dark ? .white : .black)
            .frame(height: 50).cornerRadius(8)

            Button("Continue as Guest") { /* guest path */ }
        }
        .onAppear { vm.restoreSession() }
        .onReceive(NotificationCenter.default.publisher(
            for: ASAuthorizationAppleIDProvider.credentialRevokedNotification)) { _ in
            vm.signOutLocally()
        }
    }
}
```

**Credential revocation:** observe `ASAuthorizationAppleIDProvider.credentialRevokedNotification` (fires when the user revokes in Settings → Apple Account, or when you call `/auth/revoke`). The notification can't fire when the app is terminated, so also call `getCredentialState(forUserID:)` on every cold launch.

**Storage:** the opaque `user` identifier is stable per Apple ID + Team ID. Store in Keychain. **Name and email are returned only on first sign-in** — persist them immediately.

### 5.5 Guideline 5.1.1(v) — account deletion

Verbatim: **"If your app supports account creation, you must also offer account deletion within the app."** Effective **June 30, 2022**. Requirements from Apple's *Offering account deletion in your app* guidance:

- **Easy to find** (typically in account settings).
- **Deletes the entire account record** plus associated personal data. Deactivation is insufficient.
- If completion requires the web, link to the exact completion page — not a homepage.
- **Globally available** — not limited to GDPR/CCPA jurisdictions.
- Auto-created/guest accounts must also be deletable.
- Confirmation/re-auth is allowed; **phone-call or email-ticket-only deletion is prohibited** except in highly regulated fields per 5.1.1(ix).
- For SIWA users, call the `POST https://appleid.apple.com/auth/revoke` REST endpoint with the stored refresh token (see Technote **TN3194**).

Reference UI pattern:

```swift
struct AccountSettingsView: View {
    @State private var showConfirm = false
    @State private var showFinal = false
    @State private var isDeleting = false

    var body: some View {
        Form {
            Section("Account") {
                NavigationLink("Manage Subscription") { /* AppStore.showManageSubscriptions */ }
                Button("Sign Out") { /* ... */ }
            }
            Section {
                Button(role: .destructive) { showConfirm = true } label: {
                    Label("Delete Account", systemImage: "trash")
                }
            } footer: {
                Text("Permanently deletes your account and associated data. This cannot be undone.")
            }
        }
        .confirmationDialog("Delete your account?", isPresented: $showConfirm,
                            titleVisibility: .visible) {
            Button("Continue", role: .destructive) { showFinal = true }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Permanently deletes your profile, content, and history. Cancel your subscription separately in App Store.")
        }
        .alert("Final Confirmation", isPresented: $showFinal) {
            Button("Delete Account", role: .destructive) { Task { await performDelete() } }
            Button("Cancel", role: .cancel) {}
        }
        .overlay { if isDeleting { ProgressView("Deleting…").padding().background(.regularMaterial) } }
    }

    func performDelete() async { /* fresh SIWA re-auth → DELETE /me → clear local state */ }
}
```

### 5.6 Authentication updates in iOS 18 and iOS 26

**iOS 18 (WWDC24 session 10125):** standalone Passwords app; `ASCredentialProviderViewController` enhancements for third-party credential managers; **automatic passkey upgrade API** that silently promotes a password session to a passkey after successful sign-in.

**iOS 26 (WWDC25 session 279):** new **Account Creation API** — a system-provided sign-up sheet that prefills name/email/phone and creates a passkey with one biometric confirmation; detects existing SIWA accounts to prevent duplicates. **Passkey management endpoints** (`/.well-known/passkey-endpoints`), **WebAuthn Signal API** (push username changes and revocations to credential managers), and **secure passkey import/export** across managers. For Korean subscribers, a **Korea SIWA server-to-server notification endpoint** must be registered by **January 1, 2026**.

---

## 6. Empty states

### 6.1 Two distinct types

Apple's own apps distinguish two empty state types. **First-use empty** is helpful and inviting: teach the user what to do (Reminders' empty Today list, Notes' empty folder, Safari's Reading List). **Post-action empty** is informative: the user arrived here deliberately (Mail's empty mailbox, "No results for 'xyz'"). Both follow **icon/image + title + short explanation + optional CTA**.

### 6.2 `ContentUnavailableView` (iOS 17+)

SwiftUI's standard empty-state view. Introduced WWDC23. Stable through iOS 18; unchanged in iOS 26 except for automatic Liquid Glass surface adoption.

```swift
// Type A: first-use with CTA
ContentUnavailableView {
    Label("Empty Bookmarks", systemImage: "bookmark")
} description: {
    Text("Find a great movie and bookmark it to enjoy later.")
} actions: {
    Button("Browse Movies") { browse() }.buttonStyle(.borderedProminent)
}

// Type B: post-action search empty (built-in, localized)
ContentUnavailableView.search(text: query)

// Simple convenience form
ContentUnavailableView("No Notes", systemImage: "note.text",
    description: Text("Tap the compose button to create your first note."))
```

Typical placement is an `.overlay` on a `List` when `items.isEmpty`.

### 6.3 UIKit equivalent: `UIContentUnavailableConfiguration` (iOS 17+)

Three built-in templates — `.empty()`, `.loading()`, `.search()` — applied via `UIViewController.contentUnavailableConfiguration`:

```swift
override func updateContentUnavailableConfiguration(using state: UIContentUnavailableConfigurationState) {
    if favorites.isEmpty {
        var cfg = UIContentUnavailableConfiguration.empty()
        cfg.image = UIImage(systemName: "star.slash")
        cfg.text = "No Favorites"
        cfg.secondaryText = "Your favorite items will appear here."
        var btn = UIButton.Configuration.borderedProminent()
        btn.title = "Browse"
        cfg.button = btn
        cfg.buttonProperties.primaryAction = UIAction { [weak self] _ in self?.browse() }
        contentUnavailableConfiguration = cfg
    } else {
        contentUnavailableConfiguration = nil
    }
}
```

Note that **UIKit has `.loading()` but SwiftUI does not** — for loading states in SwiftUI use `ProgressView`.

### 6.4 Pre-iOS 17 fallback

Roll your own: a `VStack` with `Image(systemName:)`, a title label (`.title2.bold()`), a secondary description (`.secondaryLabel`), and an optional `.borderedProminent` button. Wrap in `if #available(iOS 17, *)` to gate new API.

---

## 7. Error states

### 7.1 Presentation decisions

| Presentation | When to use |
|---|---|
| **Alert** (modal) | Irrecoverable or decision-requiring: destructive confirm, purchase failure, permission-blocking-flow |
| **Full-screen `ContentUnavailableView`** | The screen's primary content failed to load (network down, list unavailable) — prefer this over alerts |
| **Inline banner / under field** | Form validation errors, transient failures that don't block the whole screen |
| **Toast / temporary banner** | Non-critical self-healing events ("Saved to iCloud", "Reconnected") |
| **Action sheet** | Choices tied to a user action (HIG prefers sheets over alerts when the user triggered the choice) |

HIG principles (from *Alerts*, *Feedback*, *Progress indicators*): **minimize alerts** so users take them seriously; **describe what went wrong and suggest what to do**; **use plain language, not raw error codes**; prefer two-button alerts; button titles must be self-evident (no "explainers"); **don't blame the user.**

### 7.2 Full-screen network error with retry

```swift
struct ProductsScreen: View {
    @State private var vm = ProductsViewModel()

    var body: some View {
        Group {
            switch vm.state {
            case .loading:                     ProgressView("Loading…")
            case .loaded(let items) where items.isEmpty:
                ContentUnavailableView("No Products", systemImage: "bag",
                    description: Text("Check back later for new items."))
            case .loaded(let items):           List(items) { ProductRow(product: $0) }
            case .failed(let error):
                ContentUnavailableView {
                    Label("Can't Load Products", systemImage: "wifi.exclamationmark")
                } description: {
                    Text(error.userMessage)
                } actions: {
                    Button("Try Again") { Task { await vm.load() } }
                        .buttonStyle(.borderedProminent)
                }
            }
        }
        .task { await vm.load() }
    }
}
```

### 7.3 Inline error banner

```swift
struct ErrorBanner: View {
    let message: String
    let onRetry: (() -> Void)?
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(.orange)
            VStack(alignment: .leading, spacing: 2) {
                Text("Connection Lost").font(.subheadline).bold()
                Text(message).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if let onRetry { Button("Retry", action: onRetry).buttonStyle(.bordered).controlSize(.small) }
        }
        .padding(12)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
        .padding(.horizontal)
    }
}
```

### 7.4 Recovery action menu

Every error presentation should offer at least one of: **Retry** (primary for transient/network failures), **Report / Contact support** (persistent errors), **Dismiss / Cancel** (for modal alerts), **Use cached data / Go offline** (when applicable), **Open Settings** (for permission-related errors).

### 7.5 Anti-patterns

Avoid blaming the user, showing raw error codes (`NSURLErrorDomain -1009` alone), using vague titles like "Error", making everything modal, or using three-button alerts when an action sheet or full-screen view would fit better.

---

## 8. Loading states

### 8.1 Three patterns

| Pattern | When to use | API |
|---|---|---|
| **Indeterminate spinner** | Short, unknown-duration work | `ProgressView()` · `UIActivityIndicatorView` |
| **Determinate progress bar** | Known percentage or duration (downloads, imports) | `ProgressView(value:total:)` · `UIProgressView` |
| **Skeleton screen** | Structured content loading from the network | `.redacted(reason: .placeholder)` + shimmer |

HIG principles (*Loading*, *Progress indicators*): **show content as soon as possible** (don't wait for all data before rendering the screen); **favor progress bars over activity indicators when quantifiable**; **keep indicators moving** (a stationary spinner suggests a stall); **label indicators with meaningful text**, not vague terms like "Loading…" or "Authenticating…"; **report progress accurately** — never fake progress to look busy.

Threshold rule of thumb aligned with HIG: show feedback immediately; for tasks longer than ~1s, show a spinner; for >2–3s, show determinate progress when knowable; for structured content loads use skeletons.

### 8.2 `ProgressView` (iOS 14+)

```swift
ProgressView()                             // bare spinner
ProgressView("Loading…")                   // spinner + label

ProgressView(value: progress, total: 1.0)  // determinate
    .progressViewStyle(.linear)
    .tint(.indigo)                         // iOS 15+

ProgressView()
    .controlSize(.large)                   // iOS 15+ for larger spinner
```

Custom circular ring:

```swift
struct RingProgressStyle: ProgressViewStyle {
    var lineWidth: CGFloat = 8
    func makeBody(configuration: Configuration) -> some View {
        let fraction = configuration.fractionCompleted ?? 0
        ZStack {
            Circle().stroke(Color.secondary.opacity(0.2), lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: fraction)
                .stroke(Color.accentColor,
                        style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut, value: fraction)
        }
        .frame(width: 60, height: 60)
    }
}
```

### 8.3 Skeleton screens with `.redacted`

```swift
struct ProfileList: View {
    @State private var users: [User] = []
    @State private var isLoading = true
    private var placeholderUsers: [User] {
        Array(repeating: User(name: "Placeholder Name", title: "Placeholder subtitle"), count: 6)
    }
    var body: some View {
        List(isLoading ? placeholderUsers : users) { ProfileCard(user: $0) }
            .redacted(reason: isLoading ? .placeholder : [])
            .task { users = await load(); isLoading = false }
    }
}
```

Standard shimmer (Apple ships no built-in equivalent; this is the common implementation):

```swift
struct Shimmer: ViewModifier {
    @State private var phase: CGFloat = -1
    func body(content: Content) -> some View {
        content.mask(
            LinearGradient(
                gradient: Gradient(colors: [.black.opacity(0.3), .black, .black.opacity(0.3)]),
                startPoint: UnitPoint(x: phase, y: 0.5),
                endPoint: UnitPoint(x: phase + 1, y: 0.5)
            )
        )
        .onAppear {
            withAnimation(.linear(duration: 1.3).repeatForever(autoreverses: false)) { phase = 2 }
        }
    }
}
extension View { func shimmering(active: Bool = true) -> some View {
    Group { if active { modifier(Shimmer()) } else { self } }
}}
```

`RedactionReasons` also supports `.privacy` (iOS 15+) and `.invalidated` (iOS 17+). Read via `@Environment(\.redactionReasons)`; exclude individual children with `.unredacted()`.

### 8.4 `AsyncImage` with phases (iOS 15+)

```swift
AsyncImage(url: URL(string: "https://example.com/pic.jpg"),
           transaction: Transaction(animation: .easeInOut)) { phase in
    switch phase {
    case .empty:                  ProgressView()
    case .success(let image):     image.resizable().aspectRatio(contentMode: .fill)
    case .failure(let error):
        VStack(spacing: 8) {
            Image(systemName: "photo.badge.exclamationmark").font(.largeTitle).foregroundStyle(.secondary)
            Text(error.localizedDescription).font(.caption).multilineTextAlignment(.center)
        }
    @unknown default:             Color.gray.opacity(0.2)
    }
}
.frame(width: 200, height: 200)
.clipShape(RoundedRectangle(cornerRadius: 12))
```

Caveat: inside `List` or `LazyVStack`, `AsyncImage` downloads can be canceled on scroll (`NSURLErrorCancelled -999`); move to `ScrollView + LazyVStack` or retry on `.failure`.

### 8.5 Integrated pattern — loading → empty → error → content

```swift
struct FeedView: View {
    @State private var state: LoadState<[Post]> = .idle
    var body: some View {
        content
            .task { await load() }
            .refreshable { await load() }
    }
    @ViewBuilder private var content: some View {
        switch state {
        case .idle, .loading:
            SkeletonFeed().redacted(reason: .placeholder).shimmering()
        case .loaded(let posts) where posts.isEmpty:
            ContentUnavailableView("No Posts", systemImage: "tray")
        case .loaded(let posts):
            List(posts) { PostRow(post: $0) }
        case .failed:
            ContentUnavailableView {
                Label("Couldn't Load Feed", systemImage: "wifi.exclamationmark")
            } description: {
                Text("Check your connection and try again.")
            } actions: {
                Button("Try Again") { Task { await load() } }.buttonStyle(.borderedProminent)
            }
        }
    }
    func load() async {
        state = .loading
        do { state = .loaded(try await API.fetchPosts()) } catch { state = .failed(error) }
    }
}
```

---

## 9. Paywalls and subscriptions

### 9.1 StoreKit 2 fundamentals (iOS 15+, SK1 deprecated in iOS 18)

Modern async/await API with JWS-signed, on-device-verified transactions. Core types: **`Product`** (fetch via `Product.products(for:)`), **`Product.purchase(options:)`** → `PurchaseResult`, **`VerificationResult`** (`.verified` vs `.unverified`; never trust unverified), **`Transaction.updates`** (AsyncSequence; start in `@main` for out-of-band renewals/refunds/Ask-to-Buy), **`Transaction.currentEntitlements`** (latest valid transactions — use on launch to grant access), **`AppStore.sync()`** (restore purchases; user-initiated only).

```swift
func purchase(_ product: Product) async throws {
    let result = try await product.purchase()
    switch result {
    case .success(let verification):
        let transaction = try checkVerified(verification)
        await updateEntitlements()
        await transaction.finish()   // REQUIRED after delivering content
    case .userCancelled, .pending: break
    @unknown default: break
    }
}

let updates = Task.detached {
    for await result in Transaction.updates {
        guard case .verified(let tx) = result else { continue }
        await refreshEntitlements()
        await tx.finish()
    }
}

func refreshEntitlements() async {
    for await result in Transaction.currentEntitlements {
        guard case .verified(let tx) = result, tx.revocationDate == nil else { continue }
        purchasedIDs.insert(tx.productID)
    }
}

Button("Restore Purchases") { Task { try? await AppStore.sync() } }
```

### 9.2 Subscription APIs

`Product.SubscriptionInfo.Status` (array — one per family member when Family Sharing is enabled). **`RenewalState`**: `.subscribed`, `.expired`, `.inBillingRetryPeriod`, `.inGracePeriod`, `.revoked`. **`RenewalInfo`** exposes `willAutoRenew`, `autoRenewPreference` (detect upgrades/downgrades/cross-grades), `expirationReason`, `isInBillingRetry`, `gracePeriodExpirationDate`, `currentOfferID`, and `offerType` (`.introductory`, `.promotional`, or `.winBack` on iOS 18+).

**Offer types:**
- **Introductory offers** (new subscribers) — free trial, pay-as-you-go (discounted rate for N periods), or pay-up-front. Eligibility: `product.subscription?.isEligibleForIntroOffer(for: groupID)`.
- **Promotional offers** (existing/lapsed) — require a JWS signature from your server; supply via `options: [.promotionalOffer(offerID:signature:)]`.
- **Win-back offers** (iOS 18+) — see §9.6.

```swift
guard let statuses = try? await Product.SubscriptionInfo.status(for: groupID) else { return }
for status in statuses {
    switch status.state {
    case .subscribed, .inGracePeriod:  grantAccess()
    case .inBillingRetryPeriod:        revokeAccess(); promptUpdatePayment()
    case .expired, .revoked:           revokeAccess()
    default: break
    }
}
```

### 9.3 `SubscriptionStoreView` (iOS 17+)

WWDC23 session 10013 (*Meet StoreKit for SwiftUI*). Handles product fetch, intro-offer eligibility, localized pricing, purchase, upgrades/downgrades, and — on iOS 18+ — win-back surfacing.

```swift
import SwiftUI
import StoreKit

struct PaywallView: View {
    private let groupID = "21398470"   // from App Store Connect
    @Environment(\.dismiss) private var dismiss
    @State private var showSignIn = false

    var body: some View {
        SubscriptionStoreView(groupID: groupID) {
            VStack(spacing: 12) {
                Image(systemName: "sparkles").font(.system(size: 56, weight: .bold))
                Text("MyApp Pro").font(.largeTitle).fontWeight(.black)
                Text("Unlock every feature, sync across devices, and support ongoing development.")
                    .font(.body).multilineTextAlignment(.center)
                    .foregroundStyle(.secondary).padding(.horizontal)
                FeatureList()
            }
            .padding(.vertical, 24)
            .containerBackground(.blue.gradient, for: .subscriptionStoreHeader)
        }
        .subscriptionStoreControlStyle(.prominentPicker)   // iOS 17+
        .subscriptionStoreButtonLabel(.multiline)
        .subscriptionStorePickerItemBackground(.thinMaterial)
        .storeButton(.visible, for: .restorePurchases, .policies, .redeemCode)
        .subscriptionStorePolicyDestination(for: .termsOfService) {
            SafariWebView(url: URL(string: "https://myapp.com/terms")!)
        }
        .subscriptionStorePolicyDestination(for: .privacyPolicy) {
            SafariWebView(url: URL(string: "https://myapp.com/privacy")!)
        }
        .subscriptionStoreSignInAction { showSignIn = true }
        .sheet(isPresented: $showSignIn) { SignInView() }
        .onInAppPurchaseCompletion { _, result in
            if case .success(.success(.verified)) = result { dismiss() }
        }
    }
}
```

Key modifiers: `.subscriptionStoreControlStyle` (`.automatic | .buttons | .picker | .compactPicker | .pagedPicker | .prominentPicker` — compact and paged added in iOS 18), `.subscriptionStoreButtonLabel(.multiline | .action | .price | .displayName)`, `.storeButton(.visible, for:)`, `.subscriptionStorePolicyDestination(for:)`, `.containerBackground(_, for: .subscriptionStore | .subscriptionStoreHeader)`, `.subscriptionStatusTask(for:)`, `.onInAppPurchaseStart`, `.onInAppPurchaseCompletion`. For non-subscription products, `StoreView` lists multiple and `ProductView` merchandises one.

### 9.4 Paywall design best practices

- **Localized price + period** (use `product.displayPrice` and `product.subscription?.subscriptionPeriod`; never hardcode).
- **Explicit auto-renew disclosure**: "Renews at $X/mo until canceled. Cancel anytime in Settings."
- **Visible Restore Purchases button** — still required by App Review even though StoreKit 2 auto-syncs `currentEntitlements`.
- **Terms of Use + Privacy Policy links**, reachable from the paywall (Guideline 3.1.2 requirement via Paid Apps Agreement Schedule 2).
- **Trial clarity**: show trial length, exact charge date, and charge amount.
- **Value before price**: describe concrete benefits first; no walls of pricing ladders.
- **Same subscription group** for upgrades/downgrades so StoreKit handles proration.

**Good vs bad paywall:**

| Element | Good | Bad |
|---|---|---|
| Pricing display | Localized, includes period ("$4.99/month"); intro/trial terms inline | "Start now" with no visible price or period |
| Auto-renew | Explicit text: "Renews at $X/mo until canceled. Cancel anytime in Settings." | Buried in a web ToS link only |
| Restore | Labeled "Restore Purchases," visible in paywall and Settings | Absent, or mislabeled simply "Restore" |
| Trial conversion | Shows trial end date + first charge amount; reminder before renewal | "Free!" headline; trial converts silently at full price |
| Dismissal | Clear close (X) affordance; some content still accessible | Full-screen blocker with close control hidden or delayed |

### 9.5 App Store Review Guideline 3.1 essentials

**3.1.1 — In-App Purchase required for digital goods and unlocks.** "Apps may not use their own mechanisms to unlock content or functionality, such as license keys, augmented reality markers, QR codes, cryptocurrencies." Restore mechanism required for non-consumables and auto-renewing subs.

**3.1.2 — Subscriptions.** Minimum 7-day period; must work across all the user's devices. **3.1.2(c)** (plus Schedule 2 of the Paid Apps Agreement) requires the paywall to disclose: subscription name, length, content/services per period, price (with per-unit price), auto-renew disclosure with cancellation path, and functional in-app links to Terms of Use and Privacy Policy.

**3.1.3 — Exceptions to IAP:** reader apps (with External Link Account Entitlement), multiplatform services, enterprise services, person-to-person real-time 1:1 services, physical goods/services, free stand-alone apps, ad-management apps.

**External purchase links.** Post-Epic v. Apple (May 2025 Guidelines update), U.S. storefront apps may include external purchase buttons/links without the entitlement; **EU iOS 17.4+** allows alternative purchase methods under the DMA via `StoreKit.ExternalPurchase` / `ExternalPurchaseLink`. Other storefronts still prohibit steering outside IAP. Re-check 3.1.1(a) at every submission; it's been revised multiple times.

### 9.6 Grace periods, billing retry, and win-back (iOS 18+)

When renewal fails, the subscription enters **billing retry** for up to **60 days**. If you enable **Billing Grace Period** in App Store Connect, the subscriber retains **paid access** during the grace window — choose **3, 16, or 28 days** (weekly subs capped at 6 days). Apply to all renewals or only paid-to-paid.

Proactively notify affected users; deep-link to `Settings → Apple ID → Subscriptions` or present the `manageSubscriptionsSheet` modifier (iOS 15+).

**Win-back offers (iOS 18+, WWDC24 session 10110):** target churned subscribers. Three surfaces:

1. **Automatic App Store placement** (Manage Subscription page, product page, editorial surfaces).
2. **Automatic in-app offer sheet** via StoreKit Message API (iOS 18+; enable via Info.plist / StoreKit config).
3. **Custom merchandising** via `PurchaseIntent`:

```swift
// iOS 18+
for await intent in PurchaseIntent.intents {
    var options: Set<Product.PurchaseOption> = []
    if let offer = intent.offer, offer.type == .winBack {
        options.insert(.winBackOffer(offer))
    }
    _ = try await intent.product.purchase(options: options)
}
```

### 9.7 iOS 18 and iOS 26 StoreKit updates

**iOS 18 (WWDC24 session 10061):** Win-back offers; `SKIncludeConsumableInAppPurchaseHistory` to include finished consumables in history; new Transaction/RenewalInfo fields (`currency`, `price`, `offer`, `appTransactionID` in iOS 18.4+, globally unique per Apple Account); `SubscriptionOptionGroup`; new picker styles (`.compactPicker`, `.pagedPicker`); **Original StoreKit (SK1) deprecated**.

**iOS 26 (WWDC25 session 241):** expanded `appTransactionID` backwards-compatible to iOS 15; broader offer-code redemption contexts (`AppStore.presentOfferCodeRedeemSheet()` works back to iOS 16.3); App Store Server Library signs IAP requests server-side without hand-rolling JWS; additional `SubscriptionStoreView` customization for tiered groups.

**Liquid Glass impact on paywalls:** `SubscriptionStoreView` automatically adopts Liquid Glass materials in its picker cells, footer area, and sheet chrome on iOS 26 — another reason to prefer the system view over hand-rolled paywalls. Custom paywalls should use `.containerBackground(...)` and system materials, and verify price/disclosure text contrast because Liquid Glass translucency can reduce legibility over busy backgrounds. Respect Reduce Transparency and the iOS 26.1 Tinted/Clear toggle (Display & Brightness → Liquid Glass) — system materials honor these automatically.

### 9.8 Anti-patterns

**Don't** pre-select the most expensive tier behind a "Continue" button. **Don't** hide the dismiss control or make it tiny. **Don't** bait-and-switch trial terms. **Don't** silently convert a trial at a different price than shown. **Don't** omit the Restore Purchases button. **Don't** hide Terms and Privacy links in modal-only web popovers. **Don't** try to bypass IAP for digital content via license keys, QR codes, or crypto (3.1.1 rejection).

---

## 10. Conclusion — what actually matters

Three principles run through every topic in this reference. First, **respect user intent at first launch** — the launch screen is invisible scaffolding, onboarding is a last resort, permissions wait until they're actually needed, and sign-in is deferred until it unlocks value. Second, **use the system APIs that shipped in iOS 17 and extended through iOS 26** — `ContentUnavailableView`, `ProgressView`, `PhotosPicker`, `ContactAccessButton`, `SubscriptionStoreView`, `SignInWithAppleButton`, `.redacted(reason:)`. They embed current HIG guidance, localize automatically, and — when recompiled against iOS 26 — adopt Liquid Glass without code changes. Third, **App Review enforces the design principles** via Guidelines 2.3.3 (launch screens as screenshots), 4.8 (Sign in with Apple parity), 5.1.1(iv) (dark-pattern permissions), 5.1.1(v) (account deletion), 5.1.2 (ATT and now third-party AI disclosure as of November 2025), and 3.1.2 (subscription disclosure and restore). Treating HIG compliance as a review checklist, not a stylistic preference, is what ships.

The highest-leverage changes for apps targeting iOS 18 and iOS 26 specifically: adopt `.limited` contacts access with `ContactAccessButton` (iOS 18); use provisional notification authorization by default; migrate any lingering StoreKit 1 code before SK1 removal; ship win-back offers for churned subscribers; add the Account Creation API and passkey upgrade paths in iOS 26; and verify Liquid Glass legibility on every screen that presents prices, errors, or consent.