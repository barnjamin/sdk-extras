import sha512 from "js-sha512";
import algosdk from "algosdk";
import * as msgpack from "algo-msgpack-with-bigint";

const server = "http://localhost";
const token = "a".repeat(64);
const port = 4001;
const client = new algosdk.Algodv2(token, server, port);

const block_number = 10;

(async () => {
  let block = await client.block(block_number).do();

  for (const stxn of block.block.txns) {
    const stwad = new SignedTransactionWithAD(
      block.block.gh,
      block.block.gen,
      stxn
    );
    const regend = stwad.get_obj_for_encoding();

    if (!(await verifyProofHash(block_number, stwad))) {
      console.log("Hash doesnt match? ");
      console.log("From block", stxn);
      console.log("Regend", stwad);
    } else {
      console.log("Hash matched for", stwad.txn.txn.txID());
    }
  }
})().catch((e) => {
  console.error(e);
});

class StateDelta {
  action: number = 0;
  bytes: Uint8Array = new Uint8Array();
  uint: number | undefined = undefined;

  static fromMsgp(state_delta: any): StateDelta {
    const sd = new StateDelta();
    if ("at" in state_delta) sd.action = state_delta["at"];
    if ("bs" in state_delta) sd.bytes = state_delta["bs"];
    if ("ui" in state_delta) sd.uint = state_delta["ui"];
    return sd;
  }

  get_obj_for_encoding() {
    const obj: any = {};
    if (this.action !== 0) obj["at"] = this.action;
    if (this.bytes.length > 0) obj["bs"] = this.bytes;
    if (this.uint !== undefined) obj["ui"] = this.uint;
    return obj;
  }
}

class EvalDelta {
  global_delta: StateDelta[] = [];
  local_deltas: { [key: number]: StateDelta[] } = {};
  logs: string[] = [];
  inner_txns: SignedTransactionWithAD[] = [];

  constructor(o: {
    global_delta?: StateDelta[];
    local_deltas?: { [key: number]: StateDelta[] };
    logs?: string[];
    inner_txns?: SignedTransactionWithAD[];
  }) {}

  static fromMsgp(delta: any): EvalDelta {
    const ed = new EvalDelta({});

    if ("gd" in delta) {
      for (const idx of delta["gd"]) {
        ed.global_delta.push(StateDelta.fromMsgp(delta["gd"]));
      }
    }

    if ("ld" in delta) {
      for (const k of delta["ld"]) {
        ed.local_deltas[k].push(StateDelta.fromMsgp(delta["ld"][k]));
      }
    }

    if ("itx" in delta) {
      for (const itxn of delta["itx"]) {
        ed.inner_txns.push(
          new SignedTransactionWithAD(Buffer.from(""), "", itxn)
        );
      }
    }

    if ("lg" in delta) ed.logs = delta["lg"];

    return ed;
  }

  get_obj_for_encoding() {
    const obj: any = {};

    if (this.global_delta.length > 0)
      obj["gd"] = this.global_delta.map((gd) => {
        return gd.get_obj_for_encoding();
      });
    if (Object.keys(this.local_deltas).length > 0) obj["ld"] = {};
    if (this.logs.length > 0) obj["lg"] = this.logs;
    if (this.inner_txns.length > 0)
      obj["itx"] = this.inner_txns.map((itxn) => {
        return itxn.get_obj_for_encoding();
      });

    return obj;
  }
}

class ApplyData {
  closing_amount: number = 0;
  asset_closing_amount: number = 0;
  sender_rewards: number = 0;
  receiver_rewards: number = 0;
  close_rewards: number = 0;
  eval_delta: EvalDelta | undefined = undefined;
  config_asset: number = 0;
  application_id: number = 0;

  constructor(o: {
    closing_amount?: 0;
    asset_closing_amount?: 0;
    sender_rewards?: 0;
    receiver_rewards?: 0;
    close_rewards?: 0;
    eval_delta?: undefined;
    config_asset?: 0;
    application_id?: 0;
  }) {}

  static fromMsgp(apply_data: any): ApplyData {
    const ad = new ApplyData({});

    if ("ca" in apply_data) ad.closing_amount = apply_data["ca"];
    if ("aca" in apply_data) ad.asset_closing_amount = apply_data["aca"];
    if ("rs" in apply_data) ad.sender_rewards = apply_data["rs"];
    if ("rr" in apply_data) ad.receiver_rewards = apply_data["rr"];
    if ("rc" in apply_data) ad.close_rewards = apply_data["rc"];
    if ("caid" in apply_data) ad.config_asset = apply_data["caid"];
    if ("apid" in apply_data) ad.application_id = apply_data["apid"];
    if ("dt" in apply_data)
      ad.eval_delta = EvalDelta.fromMsgp(apply_data["dt"]);

    return ad;
  }

  get_obj_for_encoding() {
    const obj: any = {};

    if (this.closing_amount !== 0) obj["ca"] = this.closing_amount;
    if (this.asset_closing_amount !== 0) obj["aca"] = this.asset_closing_amount;
    if (this.sender_rewards !== 0) obj["rs"] = this.sender_rewards;
    if (this.receiver_rewards !== 0) obj["rr"] = this.receiver_rewards;
    if (this.close_rewards !== 0) obj["rc"] = this.close_rewards;
    if (this.config_asset !== 0) obj["caid"] = this.config_asset;
    if (this.application_id !== 0) obj["apid"] = this.application_id;
    if (this.eval_delta !== undefined)
      obj["dt"] = this.eval_delta.get_obj_for_encoding();

    return obj;
  }
}

class SignedTransactionWithAD {
  txn: algosdk.SignedTransaction;
  apply_data: ApplyData | undefined = undefined;

  constructor(gh: Buffer, gen: string, stib: any) {
    const t = stib.txn as algosdk.EncodedTransaction;
    // Manually add gh/gen to construct a correct transaction object
    t.gh = gh;
    t.gen = gen;

    const stxn = {
      txn: algosdk.Transaction.from_obj_for_encoding(t),
    } as algosdk.SignedTransaction;

    if ("sig" in stib) stxn.sig = stib.sig;
    if ("lsig" in stib) stxn.lsig = stib.lsig;
    if ("msig" in stib) stxn.msig = stib.msig;
    if ("sgnr" in stib) stxn.sgnr = stib.sgnr;

    this.txn = stxn;

    this.apply_data = ApplyData.fromMsgp(stib);
  }

  get_obj_for_encoding() {
    const txn: any = this.txn.txn.get_obj_for_encoding();
    if (txn.gen !== "") {
      delete txn.gen;
      delete txn.gh;
    }

    const obj: any = {
      txn: txn,
      ...this.apply_data?.get_obj_for_encoding(),
    };

    if (this.txn.sig) obj["sig"] = this.txn.sig;
    if (this.txn.lsig) obj["lsig"] = this.txn.lsig;
    if (this.txn.msig) obj["msig"] = this.txn.msig;
    if (this.txn.sgnr) obj["sgnr"] = this.txn.sgnr;
    if (this.txn.txn.genesisID !== "") obj["hgi"] = true;

    return obj;
  }

  hash(): Uint8Array {
    const obj = encode(this.get_obj_for_encoding());
    return hasher(obj);
  }
}

async function verifyProofHash(
  block_number: number,
  stxn: SignedTransactionWithAD
): Promise<boolean> {
  const proof = await client.getProof(block_number, stxn.txn.txn.txID()).do();
  const generated = Buffer.from(stxn.hash()).toString("base64");
  return proof.stibhash == generated;
}

function hasher(data: Uint8Array): Uint8Array {
  const tohash = concatArrays(Buffer.from("STIB"), new Uint8Array(data));
  return new Uint8Array(sha512.sha512_256.array(tohash));
}

export function concatArrays(...arrs: ArrayLike<number>[]) {
  const size = arrs.reduce((sum, arr) => sum + arr.length, 0);
  const c = new Uint8Array(size);

  let offset = 0;
  for (let i = 0; i < arrs.length; i++) {
    c.set(arrs[i], offset);
    offset += arrs[i].length;
  }

  return c;
}

export function encode(obj: Record<string | number | symbol, any>) {
  // enable the canonical option
  const options = { sortKeys: true };
  return msgpack.encode(obj, options);
}

export function decode(buffer: ArrayLike<number>) {
  return msgpack.decode(buffer);
}
