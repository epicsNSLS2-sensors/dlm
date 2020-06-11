/* aSub routines to read scope data */

#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#include <dbDefs.h>
#include <dbCommon.h>
#include <recSup.h>
#include <aSubRecord.h>
#include <epicsExport.h>

/*	Convert binary data from scope to array of epicsInt16
 *	for :WAVE:ALL:SEND?
 *	#ndddddddd	(decimal digit n followed by n decimal digits d)
 *	tt			(number of traces (lsb first))
 *	aaaaaaaa	(acquisition count)
 *		(tt iterations of the following:)
 *		TTTT		(trace number)
 *		rrrrrrrr	(reserved meaning)
 *		NNNN		(number of points)
 *		XXX...		(data)
 *
 *	for :WAVE:SEND?
 *	#ndddddddd	(decimal digit n followed by n decimal digits d)
 *	XXX...		(data)
 */

#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
volatile int dlmDebug=0;
epicsExportAddress(int, dlmDebug);

static long dlm(aSubRecord *pasub) {
	/* printf("dlm: entry\n"); */
	epicsInt8 *bytes1 = pasub->a;
	epicsInt16 *bytesPerValue = pasub->b;
	epicsInt16 *sum1 = pasub->vala;
	epicsInt32 numSum = pasub->nova;
	int i, numCountBytes, numValues, numBytes;
	epicsInt16 *wfWord;
	epicsInt8 *wfByte;

	if (dlmDebug>10) {
		for (i=0; i<40; i++) printf("%c ", bytes1[i]);
		printf("\n");
		for (i=0; i<40; i++) printf("%d ", bytes1[i]);
		printf("\n\n");
	}

	numCountBytes = bytes1[1]-'0';
	numBytes = 0;
	if (dlmDebug) printf("numCountBytes = %d, numSum=%d\n", numCountBytes, numSum);
	for (i=2; i<numCountBytes+2; i++) {
		numBytes = numBytes*10+(bytes1[i]-'0');
	}
	numValues = numBytes/ (*bytesPerValue);
	if (dlmDebug) printf("numValues = %d\n", numValues);

	if (*bytesPerValue==1) {
		wfByte = (epicsInt8 *)&bytes1[i];
		for (i=0; i<numValues; i++) {
			sum1[i] = wfByte[i];
		}
		for (; i<numSum; i++) {
			sum1[i] = 0;
		}
	} else {
		if (dlmDebug) printf("wfWord: i=%d, numValues=%d\n", i, numValues);
		wfWord = (epicsInt16 *)(&bytes1[i]);
		for (i=0; i<numValues; i++) {
			sum1[i] = wfWord[i];
		}
		if (dlmDebug) printf("wfWord: clearing rest of buffer\n");
		for (; i<numSum; i++) {
			sum1[i] = 0;
		}
	}
	return(0);
}

/*
 * a (double):		array of trace 1 (sync)
 * b (double):		array of trace 2
 * c (double):		array of trace 3
 * d (double):  	array of trace 4
 * e (int):			number of array elements
 * f (int):			increment count
 * g (double):		trigger voltage
 * h (int):			nBins
 * i (int):			eraseSums
 * j (int):			numScopeAvg
 * k (int):			sampleCriterion
 * l (double):		sampleThreshold
 * m (int):			sampleIxLow
 * n (int):			sampleIxHigh

 * o (int):			histogram off/on
 * p (int):			histNumVoltBins
 * q (double):		histVoltsLow
 * r (double):		histVoltsLowHigh

 * vala (double):	summed trace 2
 * valb (double):	summed trace 3
 * valc (double):	summed trace 4
 * vald (int):		nBins out (was found number of summed array elements)
 * vale (double):	syncVoltage
 * valf (double):	work 2
 * valg (double):	work 3
 * valh (double):	work 4
 * vali (int):		numSamples

 * valj (short):	trace2Hist
 * valk (short):	trace3Hist
 * vall (short):	trace4Hist
 */
static long dlmSum(aSubRecord *pasub) {
	/* printf("dlmSum: entry\n"); */
	double	*sync					= pasub->a;
	double	*trace2					= pasub->b;
	double	*trace3					= pasub->c;
	double	*trace4					= pasub->d;
	epicsInt32	*numElements		= pasub->e;
	epicsInt32	*incCount			= pasub->f;
	double		*triggerVoltage		= pasub->g;
	epicsInt32	*nBins				= pasub->h;
	epicsInt32	*eraseSums			= pasub->i;
	epicsInt32	*numScopeAvg		= pasub->j;
	epicsInt32	*sampleCriterion	= pasub->k;
	double		*sampleThreshold	= pasub->l;
	epicsInt32	*sampleIxLow		= pasub->m;
	epicsInt32	*sampleIxHigh		= pasub->n;
	epicsInt32	*histogram			= pasub->o;
	epicsInt32	*histNumVoltBins	= pasub->p;
	double		*histVoltsLow		= pasub->q;
	double		*histVoltsHigh		= pasub->r;
	double		*sumTrace2			= pasub->vala;
	double		*sumTrace3			= pasub->valb;
	double		*sumTrace4			= pasub->valc;
	epicsInt32	*nBinsOut			= pasub->vald;
	double		*syncVoltage		= pasub->vale;
	double		*work2				= pasub->valf;
	double		*work3				= pasub->valg;
	double		*work4				= pasub->valh;
	epicsInt32 *numSamples			= pasub->vali;
	epicsInt16 *trace2Hist			= pasub->valj;
	epicsInt16 *trace3Hist			= pasub->valk;
	epicsInt16 *trace4Hist			= pasub->vall;

	epicsInt32	nAllocElements		= pasub->noa;
	epicsInt32	nAllocSumElements	= pasub->nova;
	epicsInt32	nAllocHistElements	= pasub->novj;

	int i, j, k, counting=0, n, lastEdgeLoc, min_nBins;
	int maxFound;
	double maxTrig, minTrig, trigRange;
	double max2, max3, max4, histL, histH;
	int t2, t3, t4, vBin;

	*nBinsOut = *nBins;
	if (*eraseSums) {
		for (i=0; i<nAllocSumElements; i++) {
			sumTrace2[i] = 0;
			sumTrace3[i] = 0;
			sumTrace4[i] = 0;
			*numSamples = 0;
		}
		for (i=0; i<nAllocHistElements; i++) {
			trace2Hist[i] = 0;
			trace3Hist[i] = 0;
			trace4Hist[i] = 0;
		}
	}
	for (i=0; i<nAllocSumElements; i++) {
		work2[i] = 0;
		work3[i] = 0;
		work4[i] = 0;
		incCount[i] = 0;
	}
	if (*numElements > nAllocElements) {
		*numElements = nAllocElements;
	}
	n = *numElements;

	/* multiply by *numScopeAvg to turn that average into a sum */
	for (i=0, j=0; i<n; i++, j++) {
		sync[i] *= (*numScopeAvg);
		trace2[i] *= (*numScopeAvg);
		trace3[i] *= (*numScopeAvg);
		trace4[i] *= (*numScopeAvg);
	}

	maxTrig = -1e9;
	minTrig = 1e9;
	for (i=0; i<n; i++) {
		if (sync[i] > maxTrig) maxTrig = sync[i];
		if (sync[i] < minTrig) minTrig = sync[i];
	}
	*syncVoltage = (maxTrig + minTrig)/2.;
	trigRange = maxTrig - minTrig;
	if (fabs(*triggerVoltage) > .0001) *syncVoltage = *triggerVoltage;
	if (dlmDebug) printf("syncVoltage = %f, minTrig=%f, maxTrig=%f\n", *syncVoltage, minTrig, maxTrig);

	maxFound = 0;
	lastEdgeLoc = -10000;
	min_nBins = *nBins * .9;
	/* init histogram variables */
	max2 = -1.e9; t2 = -1;
	max3 = -1.e9; t3 = -1;
	max4 = -1.e9; t4 = -1;
	histL = (*histVoltsLow);
	histH = (*histVoltsHigh);
	for (i=0, j=0; i<n; i++, j++) {
		if (j >= nAllocSumElements) j = nAllocSumElements-1;

		/* find sync-pulse edge.  In practice, the means find peak, because acalc1 took the derivative. */
		if (i>1 && ((i-lastEdgeLoc) > min_nBins) && sync[i]>(minTrig+trigRange*.8) && sync[i]>sync[i-1] && sync[i]>sync[i+1]) {
			/* found sync pulse, but there aren't enough points left? */
			if (i >= (n-(*nBins))) break;
			j = 0; counting = 1;
			lastEdgeLoc = i;
			(*numSamples) += (*numScopeAvg);
			if (dlmDebug>1) printf("sharp = 1, sync[%d] = %f, sync[%d] = %f\n", i+1, sync[i+1], i-1, sync[i-1]);

			/* if prev sync period yielded a peak, histogram it */
			if (*histogram) {
				int ix;
				if (t2>=0 && t2<(*nBins)) {
					vBin = ((histH-max2)/(histH-histL)) * (*histNumVoltBins);
					vBin = MAX(0, MIN(vBin, (*histNumVoltBins)-1));
					ix = MAX(0, MIN(nAllocHistElements-1, vBin*(*nBins) + t2));
					++trace2Hist[ix];
				}
				if (t3>=0 && t3<(*nBins)) {
					vBin = ((histH-max3)/(histH-histL)) * (*histNumVoltBins);
					vBin = MAX(0, MIN(vBin, (*histNumVoltBins)-1));
					ix = MAX(0, MIN(nAllocHistElements-1, vBin*(*nBins) + t3));
					++trace3Hist[ix];
					if (dlmDebug) printf("hist: max3=%f, t3=%d, vBin=%d, ix=%d\n", max3, t3, vBin, ix);
				}
				if (t4>=0 && t4<(*nBins)) {
					vBin = ((histH-max4)/(histH-histL)) * (*histNumVoltBins);
					vBin = MAX(0, MIN(vBin, (*histNumVoltBins)-1));
					ix = MAX(0, MIN(nAllocHistElements-1, vBin*(*nBins) + t4));
					++trace4Hist[ix];
				}
			}

			/* See if this sample meets user criterion */
			if (*sampleCriterion) {
				/* threshold */
				counting = 0;
				for (k=i+(*sampleIxLow); k<i+(*sampleIxHigh); k++) {
					if (trace2[k] > (*sampleThreshold)) {counting = 1; break;}
					if (trace3[k] > (*sampleThreshold)) {counting = 1; break;}
					if (trace4[k] > (*sampleThreshold)) {counting = 1; break;}
				}
				if (dlmDebug) printf("i=%d, criterion %s met.\n", i, counting?"":"NOT");
			}

			if (*histogram) {
				max2 = -1.e9; t2 = -1;
				max3 = -1.e9; t3 = -1;
				max4 = -1.e9; t4 = -1;
			}
		}

		if (counting) {
			incCount[j] += 1;
			work2[j] += trace2[i];
			work3[j] += trace3[i];
			work4[j] += trace4[i];
			if (j > maxFound) {
				maxFound = j;
				if (dlmDebug>2) printf("i=%d, maxFound=%d\n", i, maxFound);
			}
			if (*histogram) {
				if (trace2[i] > max2) {max2 = trace2[i]; t2 = j;}
				if (trace3[i] > max3) {max3 = trace3[i]; t3 = j;}
				if (trace4[i] > max4) {max4 = trace4[i]; t4 = j;}
			}
		}
	}

	for (j=0; j < maxFound; j++) {
		sumTrace2[j] += work2[j];
		sumTrace3[j] += work3[j];
		sumTrace4[j] += work4[j];
		if (dlmDebug > 5) printf("work2[%d] = %f, *numScopeAvg=%d\n", j, work2[j], *numScopeAvg);
	}
	/*printf("maxFound = %d\n", maxFound);*/
	return(0);
}

#include <registryFunction.h>
#include <epicsExport.h>

static registryFunctionRef dlmRef[] = {
	{"dlm", (REGISTRYFUNCTION)dlm},
	{"dlmSum", (REGISTRYFUNCTION)dlmSum}
};

static void dlmRegister(void) {
	registryFunctionRefAdd(dlmRef, NELEMENTS(dlmRef));
}

epicsExportRegistrar(dlmRegister);
