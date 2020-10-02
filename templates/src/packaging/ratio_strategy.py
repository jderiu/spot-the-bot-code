from collections import defaultdict
import math
import random

class RatioStrategy:
    def __init__(self, convos, chunk_size, ratio, segments=[0]):
        self.convos = convos
        self.chunk_size = chunk_size
        self.ratio = ratio
        self.create_bins()
        self.segments = segments

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def create_bins(self):
        type_to_bin = defaultdict(lambda: [])
        # create_random_packages
        cid_list = []
        for result in self.convos:
            cid = str(result['_id'])
            cid_list.append(cid)
            is_human0 = result['is_human0']
            is_human1 = result['is_human1']

            if is_human0 and is_human1:
                type_to_bin['hh'].append(result)
            elif not is_human0 and not is_human1:
                type_to_bin['bb'].append(result)
            else:
                type_to_bin['hb'].append(result)
        self.type_to_bin = type_to_bin

    def chunking(self, _list, chunk_len):
        random.shuffle(_list)
        return [chunk for chunk in self.chunks(_list, chunk_len)]

    def create_chunks(self):
        n_chunks = len(self.type_to_bin['bb'])/self.chunk_size
        hh_chunk_len = math.ceil(self.chunk_size/self.ratio) #math.ceil((len(self.type_to_bin['hh']) + len(self.type_to_bin['hb']))/n_chunks)
        resample_hh = int(n_chunks*hh_chunk_len - len(self.type_to_bin['hh']) - len(self.type_to_bin['hb']))
        human_convos = self.type_to_bin['hb'] + self.type_to_bin['hh']
        bot_convos = self.type_to_bin['bb']
        if resample_hh > 0:
            resampled_hh = [random.choice(self.type_to_bin['hh']) for _ in range(resample_hh)]
            human_convos.extend(resampled_hh)
        elif resample_hh < 0:
            human_convos = random.sample(human_convos, k=len(human_convos) + resample_hh)

        convo_id_to_segments = {}
        for convo in human_convos + bot_convos:
            #we pop then the segment from the top -> we want to have a random order
            sgm = [x for x in self.segments]
            random.shuffle(sgm)
            convo_id_to_segments[str(convo['_id'])] = sgm

        for _ in range(len(self.segments)):
            bb_chunks = self.chunking(bot_convos, self.chunk_size)
            human_chunks = self.chunking(human_convos, hh_chunk_len)

            assert len(bb_chunks) == len(human_chunks)

            random.shuffle(bb_chunks)
            random.shuffle(human_chunks)

            for bb_chunk, h_chunk in zip(bb_chunks, human_chunks):
                ret_chunk = []
                for convo in bb_chunk + h_chunk:
                    convo_id = str(convo['_id'])
                    start_turn = convo_id_to_segments[convo_id].pop()
                    if start_turn == -1:
                        start_turn = len(convo['convo'])
                    if start_turn > len(convo['convo']) - 1:
                        continue
                    ret_chunk.append({'convo_id': convo_id, 'start_turn': start_turn})

                random.shuffle(ret_chunk)
                yield ret_chunk
