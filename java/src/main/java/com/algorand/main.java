package com.algorand;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

import com.SandboxAccounts;
import com.algorand.algosdk.account.Account;
import com.algorand.algosdk.account.LogicSigAccount;
import com.algorand.algosdk.builder.transaction.ApplicationCallTransactionBuilder;
import com.algorand.algosdk.builder.transaction.PaymentTransactionBuilder;
import com.algorand.algosdk.crypto.Address;
import com.algorand.algosdk.crypto.LogicsigSignature;
import com.algorand.algosdk.transaction.SignedTransaction;
import com.algorand.algosdk.transaction.Transaction;
import com.algorand.algosdk.transaction.TxGroup;
import com.algorand.algosdk.util.Encoder;
import com.algorand.algosdk.v2.client.Utils;
import com.algorand.algosdk.v2.client.common.AlgodClient;
import com.algorand.algosdk.v2.client.common.Client;
import com.algorand.algosdk.v2.client.common.Response;
import com.algorand.algosdk.v2.client.model.CompileResponse;
import com.algorand.algosdk.v2.client.model.DryrunRequest;
import com.algorand.algosdk.v2.client.model.TransactionParametersResponse;

public class main {
    public static void main(String[] args) throws Exception {
        List<Account> accts = SandboxAccounts.getSandboxAccounts();

        AlgodClient client = new AlgodClient("http://localhost", 4001, "a".repeat(64));

        LogicSigAccount lsa = getLogic(client);

        Response<TransactionParametersResponse> sp = client.TransactionParams().execute();
        TransactionParametersResponse tsp = sp.body();

        Transaction pay_txn = PaymentTransactionBuilder.Builder().amount(10000).suggestedParams(tsp)
                .sender(accts.get(0).getAddress()).receiver(lsa.getAddress()).build();

        List<Address> addrs = new ArrayList<>();
        addrs.add(accts.get(1).getAddress());

        List<Long> fassets = new ArrayList<>();
        fassets.add(11L);

        List<Long> fapps = new ArrayList<>();
        fapps.add(6L);

        Transaction app_txn = ApplicationCallTransactionBuilder.Builder().sender(accts.get(0).getAddress())
                .suggestedParams(tsp).applicationId(2L).foreignApps(fapps).foreignAssets(fassets).accounts(addrs).build();

        Transaction logic_txn = PaymentTransactionBuilder.Builder().amount(10000).suggestedParams(tsp)
                .sender(lsa.getAddress()).receiver(accts.get(0).getAddress()).build();

        // assign group ids
        Transaction[] txns = TxGroup.assignGroupID(pay_txn, app_txn, logic_txn);

        List<SignedTransaction> stxns = new ArrayList<>();
        stxns.add(accts.get(0).signTransaction(txns[0]));
        stxns.add(accts.get(0).signTransaction(txns[1]));
        stxns.add(lsa.signLogicSigTransaction(txns[2]));

        DryrunRequest drr = Utils.createDryrun(client, stxns, "", 0L, 0L);

        String fname = "java-drr.msgp";
        FileOutputStream outfile = new FileOutputStream(fname);
        outfile.write(Encoder.encodeToMsgPack(drr));
        outfile.close();

        System.out.println("Wrote to " + fname);
    }

    public static LogicSigAccount getLogic(AlgodClient client) throws Exception {

        BufferedReader br = new BufferedReader(new FileReader("/home/ben/sdk-extras/logic.teal"));
        StringBuilder sb = new StringBuilder();

        String line = br.readLine();
        while (line != null) {
            sb.append(line);
            sb.append(System.lineSeparator());
            line = br.readLine();
        }

        byte[] tealSrc = sb.toString().getBytes();

        Response<CompileResponse> compiled = client.TealCompile().source(tealSrc).execute();
        CompileResponse cr = compiled.body();

        byte[] program = Base64.getDecoder().decode(cr.result);

        LogicSigAccount lsa = new LogicSigAccount(program, null);

        return lsa;
    }
}