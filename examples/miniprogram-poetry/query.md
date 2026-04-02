> **Note:** This is a fictional task for demonstration purposes only. All app names, designs, and requirements are synthetic.

# Poetry Appreciation Mini-Program

## Implementation Constraints
- Build on the provided `uni-app` project scaffold in `files/src/`
- All code must be within the existing `src/` directory
- Do NOT create a separate native mini-program project

## 1. Visual Style
Gallery-style hand-drawn illustration aesthetic:
- Base color: warm white (#F8F6F2) with muted tones
- Textures: watercolor paper, pencil strokes
- Icons: sketchy line-art style
- Animations: gentle watercolor spread effects
- Cards: paper-edge shadows, gallery-frame layouts

## 2. Core Features

### Authentication
- Single sign-on via platform authorization (no separate registration)
- Unauthenticated users are guided to login when accessing protected features

### Home Page
- Waterfall/card layout displaying curated poetry and artwork
- Pull-to-refresh and infinite scroll
- Filter bar (by topic, dynasty/era)

### Detail Page
- Full content display for poems and artwork
- **AI Text-to-Speech (TTS)**: play/pause, speed control, voice selection, progress scrubber
- Share button (copies URL to clipboard)
- Favorite button (instant state sync)

### Community ("Gathering") Page
- Post feed with text + image posts
- Publish new post via modal form
- Like and comment with real-time count updates
- Threaded replies

### Favorites Page
- Display all favorited items (poems, art, posts)
- Filter by content type
- Single and batch unfavorite

### Navigation
- Bottom tab bar: Home | Community | Favorites | Profile
- Preserve scroll position and filter state across tab switches

## 3. Database Schema
See `task.yaml` for full schema definition and seed data.

## Output
Implement all features in the `src/` directory. The app will be tested via automated UI testing against the rubric criteria listed in `task.yaml`.
