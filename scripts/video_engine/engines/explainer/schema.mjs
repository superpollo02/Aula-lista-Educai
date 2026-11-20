import { z } from 'zod';

export const FormatoSchema = z.enum(['9:16', '16:9', '1:1', '4:5']);

export const MetaSchema = z.object({
  titulo: z.string().min(1, 'El título es obligatorio'),
  descripcion: z.string().optional(),
  formato: FormatoSchema.default('9:16'),
  estilo: z.string().default('Noche'),
  subtitulos: z.enum(['simples', 'karaoke', 'no']).default('simples'),
  ritmo: z.number().positive().default(1.35),
  cola: z.number().nonnegative().default(0.8),
  paleta: z.record(z.string()).optional(),
  fuentes: z.object({
    display: z.string().optional(),
    body: z.string().optional(),
    mono: z.string().optional(),
    googleFontsUrl: z.string().url().optional()
  }).optional()
});

export const VozSchema = z.object({
  engine: z.enum(['edge-tts', 'manual', 'whisper', 'none']).default('edge-tts'),
  locutor: z.string().default('es-AR-TomasNeural'),
  rate: z.string().default('-4%'),
  pitch: z.string().default('+0Hz'),
  pausa: z.number().nonnegative().default(0.6),
  say: z.record(z.string()).optional()
});

export const VisualDirectiveSchema = z.object({
  tipo: z.string(), // ej. 'card', 'badge', 'grid', 'padlock', 'text', 'input', 'custom'
  opciones: z.record(z.any()).optional()
});

export const EscenaSchema = z.object({
  id: z.string().optional(),
  texto: z.string().min(1, 'El texto del guion es obligatorio'),
  hablado: z.string().optional(),
  alt: z.string().default('Escena animada del explainer'),
  duracion: z.number().positive().optional(),
  inicio: z.number().nonnegative().optional(),
  cam: z.union([
    z.array(z.tuple([z.number(), z.number(), z.number(), z.number()])),
    z.string() // función o expresión JS si se define directamente
  ]).optional(),
  elementos: z.array(VisualDirectiveSchema).optional(),
  drawCode: z.string().optional() // Fragmento JS opcional con la función draw(t, F)
});

export const ExplainerSpecSchema = z.object({
  version: z.string().default('1.0'),
  meta: MetaSchema,
  voz: VozSchema.default({}),
  escenas: z.array(EscenaSchema).min(1, 'Debe haber al menos una escena')
});

export function validateExplainerSpec(data) {
  return ExplainerSpecSchema.parse(data);
}

export function safeValidateExplainerSpec(data) {
  return ExplainerSpecSchema.safeParse(data);
}
