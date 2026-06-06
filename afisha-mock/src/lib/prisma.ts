import { PrismaClient } from "@prisma/client";

/**
 * Единый экземпляр Prisma-клиента.
 * В dev-режиме Next пересоздаёт модули при hot-reload — храним клиент в globalThis,
 * чтобы не плодить подключения к БД.
 */
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
