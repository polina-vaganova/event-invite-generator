-- CreateTable
CREATE TABLE "Event" (
    "id" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "sourceUrl" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "originalTitle" TEXT,
    "image" TEXT,
    "description" TEXT,
    "genres" TEXT[],
    "date" TEXT,
    "country" TEXT,
    "duration" TEXT,
    "ageRating" TEXT,
    "director" TEXT,
    "venue" TEXT,
    "price" TEXT,
    "rating" TEXT,
    "parsedAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Event_pkey" PRIMARY KEY ("id")
);
