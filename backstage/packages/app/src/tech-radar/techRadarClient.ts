import { TechRadarApi } from '@backstage-community/plugin-tech-radar';
import { TechRadarLoaderResponse } from '@backstage-community/plugin-tech-radar-common';
import techRadarData from '../../../../tech-radar/tech-radar-data.json';
import aiRadarData from '../../../../tech-radar/ai-radar-data.json';

/**
 * Convert raw JSON data into the TechRadarLoaderResponse format.
 * Dates in timeline entries are parsed from strings to Date objects.
 */
function parseRadarData(raw: typeof techRadarData | typeof aiRadarData): TechRadarLoaderResponse {
  return {
    ...raw,
    entries: raw.entries.map(entry => ({
      ...entry,
      url: entry.url ?? '',
      timeline: entry.timeline.map(snapshot => ({
        ...snapshot,
        date: new Date(snapshot.date),
      })),
    })),
  };
}

export class CustomTechRadarClient implements TechRadarApi {
  async load(id: string | undefined): Promise<TechRadarLoaderResponse> {
    if (id === 'ai-radar') {
      return parseRadarData(aiRadarData);
    }
    return parseRadarData(techRadarData);
  }
}
