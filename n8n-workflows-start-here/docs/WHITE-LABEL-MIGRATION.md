# White-Label Migration Platform

Complete React Native to native platform migration using n8n workflows with PR-based approval gates.

---

## Table of Contents

1. [Overview](#overview)
2. [Migration Stages](#migration-stages)
3. [Agent Workflows](#agent-workflows)
4. [Configuration Assistant](#configuration-assistant)
5. [Approval Gates](#approval-gates)
6. [Generated Code Structure](#generated-code-structure)
7. [Testing Strategy](#testing-strategy)

---

## Overview

The White-Label Migration platform automates the conversion of React Native applications to native platforms (iOS, Android, Web) using a staged workflow with manual PR approval gates.

### Key Features
- 📦 Mono-repo structure generation
- 🔄 Stage-based workflow with approval gates
- 🎨 SwiftUI (iOS), Jetpack Compose (Android), React (Web)
- ✅ Automated testing and validation
- 📸 Visual diff comparison
- 📚 Auto-generated documentation

### Supported Platforms
- **iOS**: SwiftUI + Swift
- **Android**: Jetpack Compose + Kotlin
- **Web**: React + TypeScript

---

## Migration Stages

### Stage 1: Repository Scaffolding

**Webhook:** `/webhook/agent/repo-analyzer`

**Purpose:** Create initial mono-repo structure

**Actions:**
1. Clone source React Native repository
2. Create mono-repo structure:
   ```
   project-mono-repo/
   ├── ios/                # SwiftUI implementation
   ├── android/            # Jetpack Compose implementation
   ├── web/                # React implementation
   ├── shared/             # Shared business logic
   ├── contracts/          # Platform-agnostic contracts
   └── docs/               # Documentation
   ```
3. Initialize build configurations
4. Set up CI/CD pipelines

**Output:**
- GitHub repository with base structure
- **PR #1**: "Initial mono-repo scaffold"

**Approval Gate:** Manual PR approval required before Stage 2

---

### Stage 2: Analysis & Contract Generation

**Webhook:** `/webhook/agent/contract-generator`

**Purpose:** Analyze React Native code and generate platform-agnostic contracts

**Analyzes:**
- React Native components and their props
- Business logic and state management
- Data models and interfaces
- API integration patterns
- Navigation structure
- Custom hooks and utilities

**Generates:**
- **Component Contracts**: Platform-independent component specifications
- **Data Contracts**: Shared data model definitions
- **API Contracts**: Network request/response interfaces
- **Navigation Contracts**: Screen flow definitions

**Example Contract:**
```typescript
// contracts/UserProfileContract.ts
export interface UserProfileContract {
  componentName: 'UserProfile'
  props: {
    userId: string
    onUpdate: (user: User) => void
  }
  state: {
    loading: boolean
    user: User | null
    error: Error | null
  }
  methods: {
    fetchUser: () => Promise<void>
    updateProfile: (data: Partial<User>) => Promise<void>
  }
}
```

**Output:**
- `contracts/` directory with TypeScript interfaces
- Component mapping documentation
- Data flow diagrams (Mermaid)
- **PR #2**: "Component contracts and analysis"

**Approval Gate:** Manual PR approval required before Stage 3

---

### Stage 3: Code Generation

Three parallel agents generate platform-specific code:

#### iOS Transformer

**Webhook:** `/webhook/agent/code-transformer-ios`

**Generates:**
- **SwiftUI Views**: Native iOS UI components
- **ViewModels**: MVVM architecture with Combine
- **Swift Models**: Codable data models
- **Network Layer**: URLSession-based API clients
- **Navigation**: SwiftUI NavigationStack
- **Dependencies**: Swift Package Manager

**Example Output:**
```swift
// ios/Views/UserProfileView.swift
import SwiftUI
import Combine

struct UserProfileView: View {
    @StateObject private var viewModel: UserProfileViewModel

    init(userId: String) {
        _viewModel = StateObject(wrappedValue: UserProfileViewModel(userId: userId))
    }

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                UserDetailView(user: user)
            } else if let error = viewModel.error {
                ErrorView(error: error)
            }
        }
        .onAppear {
            viewModel.fetchUser()
        }
    }
}
```

**Output:** **PR #3**: "iOS implementation"

---

#### Android Transformer

**Webhook:** `/webhook/agent/code-transformer-android`

**Generates:**
- **Jetpack Compose UI**: Composable functions
- **ViewModels**: Android Architecture Components
- **Kotlin Models**: Data classes with kotlinx.serialization
- **Network Layer**: Retrofit + OkHttp
- **Navigation**: Jetpack Navigation Compose
- **Dependencies**: Gradle + Kotlin DSL

**Example Output:**
```kotlin
// android/app/src/main/java/com/app/ui/UserProfileScreen.kt
@Composable
fun UserProfileScreen(
    userId: String,
    viewModel: UserProfileViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(userId) {
        viewModel.fetchUser(userId)
    }

    when (uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> UserDetailContent(uiState.user)
        is UiState.Error -> ErrorMessage(uiState.error)
    }
}
```

**Output:** **PR #4**: "Android implementation"

---

#### Web Transformer

**Webhook:** `/webhook/agent/code-transformer-web`

**Generates:**
- **React Components**: Functional components with hooks
- **Custom Hooks**: Reusable logic hooks
- **TypeScript Interfaces**: Type-safe data models
- **API Layer**: Axios-based HTTP clients
- **Routing**: React Router v6
- **State Management**: Context API + useReducer
- **Styling**: CSS Modules or Tailwind CSS

**Example Output:**
```tsx
// web/src/components/UserProfile.tsx
import React, { useEffect } from 'react'
import { useUserProfile } from '../hooks/useUserProfile'

interface UserProfileProps {
  userId: string
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const { user, loading, error, fetchUser } = useUserProfile(userId)

  useEffect(() => {
    fetchUser()
  }, [userId, fetchUser])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  if (!user) return null

  return (
    <div className="user-profile">
      <UserDetail user={user} />
    </div>
  )
}
```

**Output:** **PR #5**: "Web implementation"

**Approval Gate:** Manual PR approval required for each platform before Stage 4

---

### Stage 4: Validation

**Webhook:** `/webhook/agent/validator`

**Purpose:** Validate generated code quality and contract compliance

**Validates:**
- **Code Quality**: Linting (SwiftLint, ktlint, ESLint)
- **Type Safety**: Swift type checker, Kotlin compiler, TypeScript
- **Contract Compliance**: All contracts implemented correctly
- **Build Success**: All platforms build without errors
- **Code Coverage**: Basic test coverage exists

**Checks:**
```bash
# iOS
xcodebuild clean build -scheme App
swiftlint lint --strict

# Android
./gradlew clean build
./gradlew ktlintCheck

# Web
npm run build
npm run lint
npm run type-check
```

**Output:**
- Validation report (markdown)
- Failed checks with remediation steps
- **PR #6**: "Validation fixes" (if issues found)

**Approval Gate:** Manual PR approval required before Stage 5

---

### Stage 5: Test Generation

**Webhook:** `/webhook/agent/test-generator`

**Purpose:** Generate comprehensive test suites for all platforms

**Generates:**

#### iOS Tests
```swift
// ios/Tests/UserProfileViewModelTests.swift
import XCTest
@testable import App

class UserProfileViewModelTests: XCTestCase {
    func testFetchUserSuccess() async {
        let viewModel = UserProfileViewModel(userId: "123")
        await viewModel.fetchUser()
        XCTAssertNotNil(viewModel.user)
        XCTAssertFalse(viewModel.isLoading)
    }
}
```

#### Android Tests
```kotlin
// android/app/src/test/java/com/app/UserProfileViewModelTest.kt
@Test
fun fetchUser_success_updatesUiState() = runTest {
    val viewModel = UserProfileViewModel()
    viewModel.fetchUser("123")

    assert(viewModel.uiState.value is UiState.Success)
}
```

#### Web Tests
```tsx
// web/src/__tests__/UserProfile.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { UserProfile } from '../components/UserProfile'

test('displays user profile after loading', async () => {
  render(<UserProfile userId="123" />)

  await waitFor(() => {
    expect(screen.getByText(/John Doe/i)).toBeInTheDocument()
  })
})
```

**Test Types:**
- **Unit Tests**: Component logic, ViewModels, hooks
- **Integration Tests**: API integration, navigation flows
- **UI Tests**: Component rendering, user interactions
- **E2E Tests**: Critical user journeys (optional)

**Output:** **PR #7**: "Test suite"

**Approval Gate:** Manual PR approval required before Stage 6

---

### Stage 6: Visual Diff

**Webhook:** `/webhook/agent/visual-diff`

**Purpose:** Compare React Native screenshots with native implementations

**Process:**
1. Capture React Native screenshots (baseline)
2. Capture iOS screenshots using XCUITest
3. Capture Android screenshots using Espresso
4. Capture Web screenshots using Playwright
5. Compare using image diff algorithms
6. Generate visual regression report

**Diff Report:**
```markdown
# Visual Regression Report

## UserProfile Screen

| Platform | Match % | Issues |
|----------|---------|--------|
| iOS      | 94%     | Font size difference in header |
| Android  | 97%     | Button color slightly off |
| Web      | 99%     | Minor spacing difference |

### iOS Diff
![iOS Diff](visual-diffs/ios-userprofile-diff.png)

Recommendations:
- Adjust header font from 18pt to 20pt
- Verify SF Pro font is loaded correctly
```

**Output:**
- Visual diff images
- Regression report (markdown)
- GitHub comment on PRs with visual diffs

---

### Stage 7: Documentation

**Webhook:** `/webhook/agent/documentation-generator`

**Purpose:** Generate comprehensive documentation

**Generates:**

#### Component Documentation
```markdown
# UserProfile Component

## iOS (SwiftUI)
**File:** `ios/Views/UserProfileView.swift`

### Props
- `userId: String` - User ID to display

### Usage
```swift
UserProfileView(userId: "123")
```

## Android (Jetpack Compose)
**File:** `android/ui/UserProfileScreen.kt`

### Parameters
- `userId: String` - User ID to display

### Usage
```kotlin
UserProfileScreen(userId = "123")
```

## Web (React)
**File:** `web/src/components/UserProfile.tsx`

### Props
```typescript
interface UserProfileProps {
  userId: string
}
```

### Usage
```tsx
<UserProfile userId="123" />
```
```

#### API Documentation
- Endpoint specifications
- Request/response examples
- Error handling guide

#### Migration Notes
- Breaking changes from React Native
- Platform-specific behaviors
- Known limitations

**Output:** **PR #8**: "Documentation"

**Final Approval Gate:** Manual PR approval required before merge

---

## Agent Workflows

### Master Orchestrator

**Workflow:** `2-master-orchestrator.json`

**Responsibilities:**
- Load migration configuration
- Track current stage
- Call agents sequentially
- Wait for PR approvals
- Update migration status
- Handle errors and rollbacks

**State Machine:**
```
SCAFFOLDING → ANALYSIS → CODE_GEN → VALIDATION → TESTING → VISUAL_DIFF → DOCS → COMPLETE
     ↓            ↓          ↓           ↓          ↓           ↓          ↓        ↓
  [PR #1]     [PR #2]  [PRs #3-5]   [PR #6]    [PR #7]     [Report]   [PR #8]  [Merge]
```

---

## Configuration Assistant

**Workflow:** `0-configuration-assistant.json`

**Webhook:** `/webhook/chat/migration-config`

**Interactive Setup:**

```
Assistant: Let's configure your white-label migration! I'll need some information.

1. What's your source React Native repository URL?
You: https://github.com/myorg/my-rn-app

2. Which platforms do you want to target? (iOS, Android, Web)
You: iOS and Android

3. What's your preferred branching strategy?
You: GitFlow (main, develop, feature branches)

4. Do you have existing platform-specific code?
You: No, pure React Native

5. What's your GitHub Personal Access Token?
You: ghp_xxxxxxxxxxxxx

6. Should we use a mono-repo or separate repos?
You: Mono-repo

7. What's the target repository name?
You: myorg/my-app-mono-repo