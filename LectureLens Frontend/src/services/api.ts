// =====================================================
// API BASE URL
// =====================================================

// LOCAL BACKEND TESTING
export const API_BASE_URL =
 "https://lecturelens-final-production.up.railway.app/";

// When you later want Railway backend, replace above with:
// export const API_BASE_URL =
//   "https://lecturelens-production-5dec.up.railway.app";


// =====================================================
// COMMON RESPONSE PARSER
// =====================================================

async function parseResponse(response: Response) {
  let data: any;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Server returned invalid response (${response.status})`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`
    );
  }

  // Backend may return HTTP 200 with success:false
  if (data?.success === false) {
    throw new Error(
      data?.message ||
      data?.error ||
      "Request failed"
    );
  }

  return data;
}


// =====================================================
// POST JSON HELPER
// =====================================================

async function postJSON(
  endpoint: string,
  body: Record<string, any>
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );

  return parseResponse(response);
}


// =====================================================
// BACKEND HEALTH CHECK
// =====================================================

export async function checkBackend() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  return parseResponse(response);
}


// =====================================================
// YOUTUBE METADATA
// =====================================================

export async function getYouTubeMetadata(
  url: string
) {
  const data = await postJSON(
    "/api/youtube/metadata",
    { url }
  );

  console.log(
    "YouTube Metadata API Response:",
    data
  );

  return data;
}


// =====================================================
// YOUTUBE TRANSCRIPT
// =====================================================

export async function getYouTubeTranscript(
  url: string
) {
  const data = await postJSON(
    "/api/youtube/transcript",
    { url }
  );

  console.log(
    "YouTube Transcript API Response:",
    data
  );

  return data;
}


// =====================================================
// AI NOTES
// =====================================================

export async function generateAINotes(
  url: string
) {
  const data = await postJSON(
    "/api/ai/notes",
    { url }
  );

  console.log(
    "AI Notes API Response:",
    data
  );

  return data;
}


// =====================================================
// AI FLASHCARDS
// =====================================================

export async function generateFlashcards(
  url: string
) {
  const data = await postJSON(
    "/api/ai/flashcards",
    { url }
  );

  console.log(
    "Flashcards API Response:",
    data
  );

  return data;
}


// =====================================================
// AI QUIZ
// =====================================================

export async function generateQuiz(
  url: string
) {
  const data = await postJSON(
    "/api/ai/quiz",
    { url }
  );

  console.log(
    "Quiz API Response:",
    data
  );

  return data;
}


// =====================================================
// AI CHAT
// =====================================================

export async function askAIChat(
  url: string,
  message: string
) {
  const data = await postJSON(
    "/api/ai/chat",
    {
      url,
      question: message,
    }
  );

  console.log(
    "AI Chat API Response:",
    data
  );

  return data;
}
