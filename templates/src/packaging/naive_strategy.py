import random

class Naive:
    def __init__(self, convos, chunk_size, segments=[0]):
        self.convos = convos
        self.chunk_size = chunk_size
        self.segments = segments

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def chunking(self, _list, chunk_len):
        random.shuffle(_list)
        return [chunk for chunk in self.chunks(_list, chunk_len)]

    def create_chunks(self):
        convo_id_to_segments = {}
        for convo in self.convos:
            # we pop then the segment from the top -> we want to have a random order
            sgm = [x for x in self.segments]
            random.shuffle(sgm)
            convo_id_to_segments[str(convo['_id'])] = sgm

        for _ in range(len(self.segments)):
            convos_chunks = self.chunking(self.convos, self.chunk_size)
            random.shuffle(convos_chunks)
            for convos_chunk in convos_chunks:
                ret_chunk = []
                for convo in convos_chunk:
                    convo_id = str(convo['_id'])
                    start_turn = convo_id_to_segments[convo_id].pop()
                    if start_turn == -1:
                        start_turn = len(convo['convo'])
                    ret_chunk.append({'convo_id': convo_id, 'start_turn': start_turn})
                random.shuffle(ret_chunk)
                yield ret_chunk

